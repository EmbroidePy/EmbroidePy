#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#

# Imports.--------------------------------------------------------------------
# -Python Imports.
import math

# -wxPython Imports.
import wx


class ZMatrix(wx.AffineMatrix2D):
    def __init__(self, *args, **kwds):
        wx.AffineMatrix2D.__init__(self)

    def Reset(self):
        wx.AffineMatrix2D.__init__(self)

    def PostScale(self, sx, sy=None, ax=0, ay=0):
        self.Invert()
        if sy is None:
            sy = sx
        if ax == 0 and ay == 0:
            self.Scale(1.0 / sx, 1.0 / sy)
        else:
            self.Translate(ax, ay)
            self.Scale(1.0 / sx, 1.0 / sy)
            self.Translate(-ax, -ay)
        self.Invert()

    def PostTranslate(self, px, py):
        self.Invert()
        self.Translate(-px, -py)
        self.Invert()

    def PostRotate(self, angle, rx=0, ry=0):
        self.Invert()
        tau = math.pi * 2
        if rx == 0 and ry == 0:
            self.Rotate(-angle * tau / 360.0)
        else:
            self.Translate(rx, ry)
            self.Rotate(-angle * tau / 360.0)
            self.Translate(-rx, -ry)
        self.Invert()

    def PreScale(self, sx, sy=None, ax=0, ay=0):
        if sy is None:
            sy = sx
        if ax == 0 and ay == 0:
            self.Scale(sx, sy)
        else:
            self.Translate(ax, ay)
            self.Scale(sx, sy)
            self.Translate(-ax, -ay)

    def PreTranslate(self, px, py):
        self.Translate(px, py)

    def PreRotate(self, angle, rx=0, ry=0):
        tau = math.pi * 2
        if rx == 0 and ry == 0:
            self.Rotate(angle * tau / 360.0)
        else:
            self.Translate(rx, ry)
            self.Rotate(angle * tau / 360.0)
            self.Translate(-rx, -ry)

    def GetScaleX(self):
        return self.Get()[0].m_11

    def GetScaleY(self):
        return self.Get()[0].m_22

    def GetSkewX(self):
        return self.Get()[0].m_12

    def GetSkewY(self):
        return self.Get()[0].m_21

    def GetTranslateX(self):
        return self.Get()[1].x

    def GetTranslateY(self):
        return self.Get()[1].y

    def InverseTransformPoint(self, position):
        self.Invert()
        converted_point = self.TransformPoint(position)
        self.Invert()
        return converted_point


class ZoomerPanel(wx.Panel):
    def __init__(self, *args, **kwds):
        self.matrix = ZMatrix()
        self.identity = ZMatrix()
        self.previous_position = None
        self._Buffer = None

        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Panel.__init__(self, *args, **kwds)

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.on_erase)

        self.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.Bind(wx.EVT_MOUSEWHEEL, self.on_mousewheel)
        self.Bind(wx.EVT_MIDDLE_DOWN, self.on_mouse_middle_down)
        self.Bind(wx.EVT_MIDDLE_UP, self.on_mouse_middle_up)

    def on_paint(self, event):
        wx.BufferedPaintDC(self, self._Buffer)

    def on_size(self, event):
        Size = self.ClientSize
        self._Buffer = wx.Bitmap(*Size)
        self.update_drawing()

    def on_erase(self, event):
        pass

    def update_drawing(self):
        dc = wx.MemoryDC()
        dc.SelectObject(self._Buffer)
        self.on_draw_background(dc)
        dc.SetTransformMatrix(self.matrix)
        self.on_draw_scene(dc)
        dc.SetTransformMatrix(self.identity)
        self.on_draw_interface(dc)
        del dc  # need to get rid of the MemoryDC before Update() is called.
        self.Refresh()
        self.Update()

    def on_draw_background(self, dc):
        pass

    def on_draw_scene(self, dc):
        pass

    def on_draw_interface(self, dc):
        pass

    def scene_matrix_reset(self):
        self.matrix.Reset()

    def scene_post_scale(self, sx, sy=None, ax=0, ay=0):
        self.matrix.PostScale(sx, sy, ax, ay)

    def scene_post_pan(self, px, py):
        self.matrix.PostTranslate(px, py)

    def scene_post_rotate(self, angle, rx=0, ry=0):
        self.matrix.PostRotate(angle, rx, ry)

    def scene_pre_scale(self, sx, sy=None, ax=0, ay=0):
        self.matrix.PreScale(sx, sy, ax, ay)

    def scene_pre_pan(self, px, py):
        self.matrix.PreTranslate(px, py)

    def scene_pre_rotate(self, angle, rx=0, ry=0):
        self.matrix.PreRotate(angle, rx, ry)

    def get_scale_x(self):
        return self.matrix.GetScaleX()

    def get_scale_y(self):
        return self.matrix.GetScaleY()

    def get_skew_x(self):
        return self.matrix.GetSkewX()

    def get_skew_y(self):
        return self.matrix.GetSkewY()

    def get_translate_x(self):
        return self.matrix.GetTranslateX()

    def get_translate_y(self):
        return self.matrix.GetTranslateY()

    def on_mousewheel(self, event):
        rotation = event.GetWheelRotation()
        mouse = event.GetPosition()
        if rotation > 1:
            self.scene_post_scale(1.1, 1.1, mouse[0], mouse[1])
        elif rotation < -1:
            self.scene_post_scale(0.9, 0.9, mouse[0], mouse[1])
        self.update_drawing()

    def on_mouse_middle_down(self, event):
        self.previous_position = event.GetPosition()

    def on_mouse_middle_up(self, event):
        self.previous_position = None

    def on_mouse_move(self, event):
        if self.previous_position is None:
            return
        scene_position = event.GetPosition()
        previous_scene_position = self.previous_position
        dx = (scene_position[0] - previous_scene_position[0])
        dy = (scene_position[1] - previous_scene_position[1])
        self.scene_post_pan(dx, dy)
        self.update_drawing()
        self.previous_position = scene_position

    def focus_position_scene(self, scene_point):
        window_width, window_height = self.ClientSize
        scale_x = self.get_scale_x()
        scale_y = self.get_scale_y()
        self.scene_matrix_reset()
        self.scene_post_pan(-scene_point[0], -scene_point[1])
        self.scene_post_scale(scale_x, scale_y)
        self.scene_post_pan(window_width / 2.0, window_height / 2)

    def focus_viewport_scene(self, new_scene_viewport, buffer=0.1, lock=True):
        window_width, window_height = self.ClientSize
        left = new_scene_viewport[0]
        top = new_scene_viewport[1]
        right = new_scene_viewport[2]
        bottom = new_scene_viewport[3]
        viewport_width = right - left
        viewport_height = bottom - top
        if viewport_width == 0:
            viewport_width = 1
        if viewport_height == 0:
            viewport_height = 1
        left -= viewport_width * buffer
        right += viewport_width * buffer
        top -= viewport_height * buffer
        bottom += viewport_height * buffer

        scale_x = window_width / float(right - left)
        scale_y = window_height / float(bottom - top)

        cx = ((right + left) / 2)
        cy = ((top + bottom) / 2)
        self.matrix.Reset()
        self.matrix.PostTranslate(-cx, -cy)
        if lock:
            scale = min(scale_x, scale_y)
            self.matrix.PostScale(scale)
        else:
            self.matrix.PostScale(scale_x, scale_y)
        self.matrix.PostTranslate(window_width / 2.0, window_height / 2.0)

    def convert_scene_to_window(self, position):
        return self.matrix.TransformPoint([position[0], position[1]])

    def convert_window_to_scene(self, position):
        return self.matrix.InverseTransformPoint([position[0], position[1]])
