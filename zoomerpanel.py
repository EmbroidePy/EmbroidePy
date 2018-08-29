#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#

# Imports.--------------------------------------------------------------------
# -Python Imports.
import math

# -wxPython Imports.
import wx

USE_BUFFERED_DC = True


class ZoomerPanel(wx.Panel):
    def __init__(self, *args, **kwds):
        self.matrix = wx.AffineMatrix2D()
        self.identity = wx.AffineMatrix2D()
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
        # All that is needed here is to draw the buffer to screen
        if USE_BUFFERED_DC:
            dc = wx.BufferedPaintDC(self, self._Buffer)
        else:
            dc = wx.PaintDC(self)
            dc.DrawBitmap(self._Buffer, 0, 0)

    def on_size(self, event):
        Size = self.ClientSize
        self._Buffer = wx.Bitmap(*Size)
        self.update_drawing()

    def on_erase(self, event):
        pass

    def update_drawing(self):
        """
        This would get called if the drawing needed to change, for whatever reason.

        The idea here is that the drawing is based on some data generated
        elsewhere in the system. If that data changes, the drawing needs to
        be updated.

        This code re-draws the buffer, then calls Update, which forces a paint event.
        """
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
        self.matrix = wx.AffineMatrix2D()

    def scene_post_scale(self, sx, sy=None, ax=0, ay=0):
        self.matrix.Invert()
        if sy is None:
            sy = sx
        if ax == 0 and ay == 0:
            self.matrix.Scale(sx, sy)
        else:
            self.matrix.Translate(ax, ay)
            self.matrix.Scale(sx, sy)
            self.matrix.Translate(-ax, -ay)

        self.matrix.Invert()

    def scene_post_pan(self, px, py):
        self.matrix.Invert()
        self.matrix.Translate(px, py)
        self.matrix.Invert()

    def scene_post_rotate(self, angle, rx=0, ry=0):
        self.matrix.Invert()
        tau = math.pi * 2
        if rx == 0 and ry == 0:
            self.matrix.Rotate(angle * tau / 360.0)
        else:
            self.matrix.Translate(rx, ry)
            self.matrix.Rotate(angle * tau / 360.0)
            self.matrix.Translate(-rx, -ry)
        self.matrix.Invert()

    def scene_pre_scale(self, sx, sy=None, ax=0, ay=0):
        if sy is None:
            sy = sx
        if ax == 0 and ay == 0:
            self.matrix.Scale(sx, sy)
        else:
            self.matrix.Translate(ax, ay)
            self.matrix.Scale(sx, sy)
            self.matrix.Translate(-ax, -ay)

    def scene_pre_pan(self, px, py):
        self.matrix.Translate(px, py)

    def scene_pre_rotate(self, angle, rx=0, ry=0):
        tau = math.pi * 2
        if rx == 0 and ry == 0:
            self.matrix.Rotate(angle * tau / 360.0)
        else:
            self.matrix.Translate(rx, ry)
            self.matrix.Rotate(angle * tau / 360.0)
            self.matrix.Translate(-rx, -ry)

    def get_scale_x(self):
        return self.matrix.Get()[0].m_11

    def get_scale_y(self):
        return self.matrix.Get()[0].m_22

    def get_skew_x(self):
        return self.matrix.Get()[0].m_12

    def get_skew_y(self):
        return self.matrix.Get()[0].m_21

    def get_translate_x(self):
        return self.matrix.Get()[1].x

    def get_translate_y(self):
        return self.matrix.Get()[1].y

    def on_mousewheel(self, event):
        rotation = event.GetWheelRotation()
        mouse = event.GetPosition()
        if rotation > 1:
            self.scene_post_scale(1.1, 1.1, mouse[0], mouse[1])
            # self.scene_post_rotate(-10, mouse[0], mouse[1])
        elif rotation < -1:
            self.scene_post_scale(0.9, 0.9, mouse[0], mouse[1])
            # self.scene_post_rotate(10, mouse[0], mouse[1])
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

        self.scene_post_pan(-dx, -dy)
        self.update_drawing()
        self.previous_position = scene_position

    def focus_position_scene(self, px, py):
        client_size = self.ClientSize
        center = [client_size[0] / 2.0, client_size[1] / 2.0]
        dx = center[0] - px
        dy = center[1] - py
        self.scene_post_pan(dx, dy)

    def convert_scene_to_window(self, position):
        return self.matrix.TransformPoint(position[0], position[1])

    def convert_window_to_scene(self, position):
        self.matrix.Invert()
        converted_point = self.invert_matrix.TransformPoint(position[0], position[1])
        self.matrix.Invert()
        return converted_point
