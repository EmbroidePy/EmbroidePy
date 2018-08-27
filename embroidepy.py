#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.8.3 on Thu Aug 09 23:03:17 2018
#

# Imports.--------------------------------------------------------------------
# -Python Imports.
import os
import sys
import math

# -wxPython Imports.
import wx
import wx.grid
import wx.lib.agw.aui as aui

# -pyembroidery Imports.
import pyembroidery
from pyembroidery.CsvWriter import get_common_name_dictionary
from pyembroidery.CsvReader import get_command_dictionary
from pyembroidery.EmbConstant import *

USE_BUFFERED_DC = True


class ZoomerPanel(wx.Panel):
    def __init__(self, *args, **kwds):
        self.matrix = wx.AffineMatrix2D()
        self.invert_matrix = wx.AffineMatrix2D()
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
        self.on_draw_interface(dc)
        dc.SetTransformMatrix(self.matrix)
        self.on_draw_scene(dc)
        del dc  # need to get rid of the MemoryDC before Update() is called.
        self.Refresh()
        self.Update()

    def on_draw_scene(self, dc):
        pass

    def on_draw_interface(self, dc):
        pass

    def scene_matrix_reset(self):
        self.matrix = wx.AffineMatrix2D()

    def scene_post_scale(self, sx, sy=None):
        if sy is None:
            self.matrix.Scale(sx, sx)
        else:
            self.matrix.Scale(sx, sy)

    def scene_post_pan(self, px, py):
        self.matrix.Translate(px, py)

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
        mouse = self.convert_window_to_scene(event.GetPosition())
        self.scene_post_pan(mouse[0], mouse[1])
        if rotation > 1:
            self.scene_post_scale(1.1)
        elif rotation < -1:
            self.scene_post_scale(0.9, 0.9)
        self.scene_post_pan(-mouse[0], -mouse[1])
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
        dx = (scene_position[0] - previous_scene_position[0]) / self.get_scale_x()
        dy = (scene_position[1] - previous_scene_position[1]) / self.get_scale_y()

        self.scene_post_pan(dx, dy)
        self.update_drawing()
        self.previous_position = scene_position

    def focus_position_scene(self, px, py):
        client_size = self.ClientSize
        center = self.convert_window_to_scene([client_size[0] / 2, client_size[1] / 2])
        dx = center[0] - px
        dy = center[1] - py
        self.scene_post_pan(dx, dy)

    def convert_scene_to_window(self, position):
        return self.matrix.TransformPoint(position[0], position[1])

    def convert_window_to_scene(self, position):
        self.invert_matrix = wx.AffineMatrix2D()
        self.invert_matrix.Concat(self.matrix)
        self.invert_matrix.Invert()
        return self.invert_matrix.TransformPoint(position[0], position[1])


class EmbroideryView(ZoomerPanel):
    def __init__(self, *args, **kwds):
        self.draw_data = None
        self.emb_pattern = None
        self.buffer = 0.1
        self._Buffer = None
        self.current_stitch = -1
        self.selected_point = None
        self.drag_point = None
        self.clicked_position = None
        self.previous_position = None
        self.name_dict = get_common_name_dictionary()
        self.track = False

        # begin wxGlade: EmbroideryView.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE | wx.WANTS_CHARS
        ZoomerPanel.__init__(self, *args, **kwds)

        # end wxGlade

        self.Bind(wx.EVT_KEY_DOWN, self.on_key_press)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_left_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_mouse_left_up)
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_left_double_click)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_right_mouse_down)

        # OnSize called to make sure the buffer is initialized.
        # This might result in OnSize getting called twice on some
        # platforms at initialization, but little harm done.
        self.on_size(None)
        self.paint_count = 0

    def on_mouse_move(self, event):
        ZoomerPanel.on_mouse_move(self, event)
        if self.drag_point is None:
            return
        self.clicked_position = self.convert_window_to_scene(event.GetPosition())
        mod_stitch = self.emb_pattern.stitches[self.drag_point]
        mod_stitch[0] = self.clicked_position[0]
        mod_stitch[1] = self.clicked_position[1]
        self.draw_data = None
        self.update_drawing()

    def on_mouse_left_down(self, event):
        self.previous_position = event.GetPosition()
        self.clicked_position = self.convert_window_to_scene(self.previous_position)
        self.SetFocus()
        if self.emb_pattern is None:
            return
        nearest = self.get_nearest_point(self.clicked_position)
        if nearest[1] > 25:
            event.Skip()
            self.drag_point = None
            return
        best_index = nearest[0]
        self.drag_point = best_index
        self.selected_point = best_index

    def on_mouse_left_up(self, event):
        self.clicked_position = None
        self.previous_position = None
        self.drag_point = None
        self.update_drawing()

    def on_left_double_click(self, event):
        self.clicked_position = self.convert_window_to_scene(event.GetPosition())
        nearest = self.get_nearest_point(self.clicked_position)
        if nearest[0] is None:
            position = self.convert_window_to_scene(self.clicked_position)
            stitches = self.emb_pattern.stitches
            stitches.append([position[0], position[1], pyembroidery.STITCH])
            self.selected_point = 0
            self.draw_data = None
            self.update_drawing()
            return
        if nearest[1] > 25:
            if self.selected_point is None:
                return
            stitches = self.emb_pattern.stitches
            stitch = stitches[self.selected_point]
            new_stitch = stitch[:]
            position = self.clicked_position
            new_stitch[0] = position[0]
            new_stitch[1] = position[1]
            stitches.insert(self.selected_point + 1, new_stitch)
            self.selected_point += 1
            self.draw_data = None
            self.update_drawing()
            return
        best_index = nearest[0]
        stitches = self.emb_pattern.stitches
        stitch = stitches[best_index]
        stitches.insert(best_index, stitch[:])
        self.selected_point = best_index
        self.draw_data = None
        self.update_drawing()

    def on_right_mouse_down(self, event):
        self.clicked_position = self.convert_window_to_scene(event.GetPosition())
        nearest = self.get_nearest_point(self.clicked_position)
        menu = wx.Menu()
        if nearest[1] <= 25:
            menu_item = menu.Append(wx.ID_ANY, "Delete", "")
            self.Bind(wx.EVT_MENU, self.on_menu_delete, menu_item)
            menu_item = menu.Append(wx.ID_ANY, "Duplicate", "")
            self.Bind(wx.EVT_MENU, self.on_menu_duplicate, menu_item)
        else:
            menu_item = menu.Append(wx.ID_ANY, "Track", "", wx.ITEM_CHECK)
            if self.track:
                # menu_item.SetChecked(self.track)
                pass
            self.Bind(wx.EVT_MENU, self.on_menu_track, menu_item)
        self.PopupMenu(menu)
        menu.Destroy()

    def on_menu_track(self, event):
        self.track = not self.track

    def on_menu_delete(self, event):
        best_index = self.get_nearest_point(self.clicked_position)[0]
        stitches = self.emb_pattern.stitches
        del stitches[best_index]
        self.selected_point = None
        self.draw_data = None
        self.update_drawing()

    def on_menu_duplicate(self, event):
        best_index = self.get_nearest_point(self.clicked_position)[0]
        stitches = self.emb_pattern.stitches
        stitch = stitches[best_index]
        stitches.insert(best_index, stitch[:])
        self.selected_point = best_index
        self.draw_data = None
        self.update_drawing()

    def on_key_press(self, event):
        keycode = event.GetKeyCode()
        stitch_max = len(self.emb_pattern.stitches)
        if keycode in [81, 113]:
            stitches = self.emb_pattern.stitches
            stitch = stitches[self.selected_point]
            if stitch[2] != SEQUIN_EJECT:
                stitch[2] = SEQUIN_EJECT
            else:
                stitch[2] = STITCH
            self.draw_data = None
            self.update_drawing()
        elif keycode in [wx.WXK_ESCAPE]:
            self.selected_point = None
            self.update_drawing()
        elif keycode in [68, wx.WXK_RIGHT, wx.WXK_NUMPAD6]:
            if self.selected_point is None:
                self.selected_point = 0
            else:
                self.selected_point += 1
            if self.selected_point >= stitch_max:
                self.selected_point = stitch_max - 1
            if self.track:
                stitches = self.emb_pattern.stitches
                if len(stitches) == 0:
                    return
                stitch = stitches[self.selected_point]
                self.focus_position_scene(stitch[0], stitch[1])

            self.update_drawing()
        elif keycode in [65, wx.WXK_LEFT, wx.WXK_NUMPAD4]:
            if self.selected_point is None:
                self.selected_point = stitch_max - 1
            else:
                self.selected_point -= 1
            if self.selected_point < 0:
                self.selected_point = 0
            if self.track:
                stitches = self.emb_pattern.stitches
                if len(stitches) == 0:
                    return
                stitch = stitches[self.selected_point]
                self.focus_position_scene(stitch[0], stitch[1])

            self.update_drawing()
        elif keycode in [127]:
            if self.selected_point is None:
                return
            stitches = self.emb_pattern.stitches
            del stitches[self.selected_point]
            stitch_max = len(self.emb_pattern.stitches)
            if self.selected_point >= stitch_max:
                self.selected_point = stitch_max - 1
            if stitch_max == 0:
                self.selected_point = None
            if self.track:
                stitches = self.emb_pattern.stitches
                stitch = stitches[self.selected_point]
                self.focus_position_scene(stitch[0], stitch[1])
            self.draw_data = None
            self.update_drawing()
        elif keycode in [32]:
            if self.selected_point is None:
                return
            stitches = self.emb_pattern.stitches
            stitch = stitches[self.selected_point]
            self.focus_position_scene(stitch[0], stitch[1])
            self.update_drawing()

    def create_draw_data(self):
        stitches = self.emb_pattern.stitches
        draw_data = []
        color_index = 0
        color = self.emb_pattern.get_thread_or_filler(color_index)
        color_index += 1
        lines = []
        trimmed = True
        command = NO_COMMAND

        i = -1
        ie = len(stitches) - 2
        while i < ie:
            i += 1
            current = stitches[i]
            next = stitches[i + 1]
            lines.append([current[0], current[1], next[0], next[1]])
            command = current[2]
            if command == COLOR_CHANGE:
                color = self.emb_pattern.get_thread_or_filler(color_index)
                color_index += 1
            if command == next[2]:
                continue
            if command == STITCH or command == SEQUIN_EJECT or command == SEW_TO or command == NEEDLE_AT:
                trimmed = False
            elif command == TRIM or command == COLOR_CHANGE or command == COLOR_BREAK or command == SEQUENCE_BREAK:
                trimmed = True
            draw_data.append((
                (color.get_red(), color.get_green(), color.get_blue()),
                lines,
                command,
                trimmed))
            lines = []

        if len(lines) > 0:
            draw_data.append((
                (color.get_red(), color.get_green(), color.get_blue()),
                lines,
                command,
                trimmed))
        return draw_data

    def on_draw_interface(self, dc):
        dc.SetBackground(wx.Brush("Grey"))
        dc.Clear()
        if self.selected_point is not None:
            mod_stitch = self.emb_pattern.stitches[self.selected_point]
            name = self.name_dict[mod_stitch[2]] + " " + str(self.selected_point)
            dc.DrawText(name, 0, 0)

    def on_draw_scene(self, dc):
        if self.emb_pattern is None:
            return
        # Since the pan and zoom is implemented in the canvas this can be maintained stablized.
        if self.draw_data is None:
            self.draw_data = self.create_draw_data()
        draw_data = self.draw_data
        current_stitch = self.current_stitch
        # Here's the actual drawing code.

        scale_x = self.get_scale_x()
        scale_bit = math.pow(self.get_scale_x(), -0.6)

        count = 0
        count_range = 0
        for drawElements in draw_data:
            pen = wx.Pen(drawElements[0])
            if drawElements[3]:
                pen.SetStyle(wx.PENSTYLE_DOT)
            else:
                pen.SetStyle(wx.PENSTYLE_SOLID)
            if drawElements[2] == SEQUIN_EJECT:
                dc.SetBrush(wx.Brush("Gold"))
                dc.SetPen(wx.TRANSPARENT_PEN)
                lines = drawElements[1]
                for line in lines:
                    dc.DrawCircle(line[0], line[1], 25)
            pen.SetWidth(3 * scale_bit)
            dc.SetPen(pen)
            count_range += len(drawElements[1])
            if current_stitch != -1 and current_stitch < count_range:
                dif = current_stitch - count
                segments = drawElements[1]
                subsegs = segments[:dif]
                dc.DrawLineList(subsegs)
                break
            else:
                dc.DrawLineList(drawElements[1])
            count = count_range

        if self.selected_point is not None:
            mod_stitch = self.emb_pattern.stitches[self.selected_point]
            dc.SetBrush(wx.Brush("Green"))
            scene_point = mod_stitch
            dc.GetPen().SetWidth(1)
            dc.GetPen().SetStyle(wx.PENSTYLE_SOLID)
            dc.DrawCircle(scene_point[0], scene_point[1], 10 * scale_bit)

    def update_affine(self, width, height):
        self.scene_matrix_reset()
        extends = self.emb_pattern.extends()
        min_x = min(extends[0], 50)
        min_y = min(extends[1], -50)
        max_x = max(extends[2], 50)
        max_y = max(extends[3], -50)

        embroidery_width = (max_x - min_x) + (width * self.buffer)
        embroidery_height = (max_y - min_y) + (height * self.buffer)
        scale_x = float(width) / embroidery_width
        scale_y = float(height) / embroidery_height
        translate_x = -min_x + (width * self.buffer) / 2
        translate_y = -min_y + (height * self.buffer) / 2
        self.scene_post_scale(min(scale_x, scale_y))
        self.scene_post_pan(translate_x, translate_y)

    def update_affines(self):
        Size = self.ClientSize
        try:
            self.update_affine(Size[0], Size[1])
        except (AttributeError, TypeError):
            pass

    def on_size(self, event):
        self.draw_data = None
        self.update_affines()
        ZoomerPanel.on_size(self, event)

    def set_design(self, set_design):
        self.emb_pattern = set_design
        self.update_drawing()

    @staticmethod
    def distance_sq(p0, p1):
        dx = p0[0] - p1[0]
        dy = p0[1] - p1[1]
        dx *= dx
        dy *= dy
        return dx + dy

    def get_nearest_point(self, position):
        best_point = None
        best_index = None
        best_distance = sys.maxint
        for i, stitch in enumerate(self.emb_pattern.stitches):
            distance = self.distance_sq(position, stitch)
            if best_point is None or distance < best_distance or (
                    distance == best_distance and self.selected_point == i):
                best_point = stitch
                best_distance = distance
                best_index = i
        return best_index, best_distance, best_point


# end of class EmbroideryView


class SimulatorView(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: SimulatorView.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((845, 605))
        self.stitch_slider = wx.Slider(self, wx.ID_ANY, 0, 0, 10)
        self.Bind(wx.EVT_SCROLL_CHANGED, self.on_slider_changed, self.stitch_slider)
        self.canvas = EmbroideryView(self, wx.ID_ANY)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        # Menu Bar
        self.frame_menubar = wx.MenuBar()

        wxglade_tmp_menu = wx.Menu()
        menu_start = wxglade_tmp_menu.Append(wx.ID_ANY, "Start", "")
        self.Bind(wx.EVT_MENU, self.on_menu_start, menu_start)
        self.menu_start = menu_start
        menu_backwards = wxglade_tmp_menu.Append(wx.ID_ANY, "Backwards", "", wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.on_menu_backwards, menu_backwards)
        menu_track = wxglade_tmp_menu.Append(wx.ID_ANY, "Track", "", wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.on_menu_track, menu_track)

        self.frame_menubar.Append(wxglade_tmp_menu, "Options")
        self.SetMenuBar(self.frame_menubar)
        # Menu Bar end

        self.__set_properties()
        self.__do_layout()
        # end wxGlade
        self.design = None
        self.track = False
        self.forwards = True
        self.timer = None

    def on_slider_changed(self, event):
        self.canvas.current_stitch = event.GetPosition()
        self.canvas.update_drawing()

    def on_menu_start(self, event):
        if not self.timer:
            self.timer = wx.PyTimer(self.update_tick)
            self.timer.Start(30)
            self.menu_start.SetItemLabel("Stop")
        else:
            self.timer.Stop()
            self.timer = None
            self.menu_start.SetItemLabel("Start")

    def on_menu_track(self, event):
        self.track = not self.track

    def on_menu_forwards(self, event):
        self.forwards = True

    def on_menu_backwards(self, event):
        self.forwards = not self.forwards

    def on_close(self, event):
        if self.timer is not None:
            self.timer.Stop()
        event.Skip()

    def update_tick(self):
        if self.forwards:
            self.increment_stitch()
        else:
            self.decrement_stitch()
        self.stitch_slider.SetValue(self.canvas.current_stitch)
        self.canvas.update_drawing()

    def OnErase(self, event):
        pass

    def __set_properties(self):
        # begin wxGlade: SimulatorView.__set_properties
        self.SetTitle("Simulator")
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: SimulatorView.__do_layout
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_3.Add(self.stitch_slider, 0, wx.EXPAND, 0)
        sizer_3.Add(self.canvas, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_3)
        self.Layout()
        # end wxGlade

    def set_design(self, set_design):
        self.design = set_design
        self.canvas.set_design(set_design)
        self.stitch_slider.SetMax(len(self.canvas.emb_pattern.stitches))
        self.stitch_slider.SetMin(0)

    def decrement_stitch(self):
        self.canvas.current_stitch -= 1
        if self.canvas.current_stitch < 0:
            self.canvas.current_stitch = len(self.canvas.emb_pattern.stitches)

    def increment_stitch(self):
        self.canvas.current_stitch += 1
        if self.canvas.current_stitch > len(self.canvas.emb_pattern.stitches):
            self.canvas.current_stitch = 0


# end of class SimulatorView


class StitchEditor(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: StitchEditor.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.design = None
        self.SetSize((597, 627))

        self.grid = wx.grid.Grid(self, wx.ID_ANY, size=(1, 1))
        self.grid.Bind(wx.grid.EVT_GRID_LABEL_RIGHT_CLICK,
                       self.show_popup_menu_label)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK,
                       self.show_popup_menu_cell)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.on_grid_change)

        self.__set_properties()
        self.__do_layout()
        self.last_event = None
        self.command_menu = {}
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: StitchEditor.__set_properties
        self.SetTitle("Stitch Editor")
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: StitchEditor.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(self.grid, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        self.Layout()
        # end wxGlade

    def on_grid_change(self, event):
        row = event.GetRow()
        col = event.GetCol()
        value = self.grid.GetCellValue(row, col)
        stitches = self.design.emb_pattern.stitches
        stitch = stitches[row]

        if col == -1:
            return
        elif col == 0:
            command_dict = get_command_dictionary()
            command = command_dict[value]
            stitch[2] = command
        elif col == 1:
            stitch[0] = float(value)
        elif col == 2:
            stitch[1] = float(value)

    def show_popup_menu_label(self, event):
        self.last_event = event
        menu = wx.Menu()

        menu_item = menu.Append(wx.ID_ANY, "Delete", "")
        self.Bind(wx.EVT_MENU, self.on_menu_delete, menu_item)

        menu_item = menu.Append(wx.ID_ANY, "Duplicate", "")
        self.Bind(wx.EVT_MENU, self.on_menu_duplicate, menu_item)

        self.PopupMenu(menu)
        menu.Destroy()

    def show_popup_menu_cell(self, event):
        self.last_event = event
        col = event.GetCol()
        if col != 0:
            return
        row = event.GetRow()
        stitches = self.design.stitches
        stitch = stitches[row]

        self.last_event = event
        menu = wx.Menu()
        name_dict = get_common_name_dictionary()

        for the_key, the_value in name_dict.items():
            menu_item = menu.Append(the_key, the_value, the_value)
            self.Bind(wx.EVT_MENU, self.on_menu_cell_key, menu_item)
        self.PopupMenu(menu)
        menu.Destroy()

    def on_menu_cell_key(self, event):
        col = self.last_event.GetCol()
        row = self.last_event.GetRow()
        stitches = self.design.stitches
        stitch = stitches[row]
        name_dict = get_common_name_dictionary()
        command = event.GetId()
        command_name = name_dict[command]
        stitch[2] = command
        self.grid.SetCellValue(row, col, command_name)

    def on_menu_delete(self, event):
        stitches = self.design.stitches
        position = self.last_event.GetRow()
        del stitches[position]
        self.grid.DeleteRows(position)

    def on_menu_duplicate(self, event):
        stitches = self.design.stitches
        position = self.last_event.GetRow()
        stitch = stitches[position]
        stitches.insert(position, stitch[:])
        self.grid.InsertRows(position)
        common_dict = get_common_name_dictionary()
        common_name = common_dict[stitch[2]]
        self.grid.SetCellValue(position, 0, common_name)
        self.grid.SetCellValue(position, 1, str(stitch[0]))
        self.grid.SetCellValue(position, 2, str(stitch[1]))

    def set_design(self, set_design):
        self.design = set_design
        if self.design is not None:
            max = len(self.design.stitches)
        else:
            max = 0
        self.grid.CreateGrid(max, 3)
        self.grid.EnableDragColSize(0)
        self.grid.EnableDragRowSize(0)
        self.grid.EnableDragGridSize(0)
        self.grid.SetColLabelValue(0, "Command")
        self.grid.SetColLabelValue(1, "X")
        self.grid.SetColLabelValue(2, "Y")

        common_dict = get_common_name_dictionary()
        for i, stitch in enumerate(self.design.stitches):
            common_name = common_dict[stitch[2]]
            self.grid.SetCellValue(i, 0, common_name)
            self.grid.SetCellValue(i, 1, str(stitch[0]))
            self.grid.SetCellValue(i, 2, str(stitch[1]))

    # end of class StitchEditor


class ColorEmbroidery(wx.Panel):
    def __init__(self, *args, **kwds):
        # begin wxGlade: ColorEmbroidery.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Panel.__init__(self, *args, **kwds)
        self.SetSize((400, 300))
        # self.tree_ctrl_1 = wx.TreeCtrl(self, wx.ID_ANY)
        # This was intended to display color information.
        self.canvas = EmbroideryView(self, wx.ID_ANY)

        self.__do_layout()
        self.design = None
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: ColorEmbroidery.__do_layout
        sizer_6 = wx.BoxSizer(wx.HORIZONTAL)
        # sizer_6.Add(self.tree_ctrl_1, 1, wx.EXPAND, 0)
        sizer_6.Add(self.canvas, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_6)
        self.Layout()
        # end wxGlade

    def set_design(self, set_design):
        self.design = set_design
        self.canvas.set_design(self.design)


# end of class ColorEmbroidery

class BaseAuiNotebook(aui.AuiNotebook):
    """
    Base AuiNotebook

    :seealso: http://wxpython.org/Phoenix/docs/html/lib.agw.aui.auibook.AuiNotebook.html
    """

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=0
                 ,
                 agwStyle=  # aui.AUI_NB_DEFAULT_STYLE |         #AUI_NB_DEFAULT_STYLE = AUI_NB_TOP | AUI_NB_TAB_SPLIT | AUI_NB_TAB_MOVE | AUI_NB_SCROLL_BUTTONS | AUI_NB_CLOSE_ON_ACTIVE_TAB | AUI_NB_MIDDLE_CLICK_CLOSE | AUI_NB_DRAW_DND_TAB
                 aui.AUI_NB_TOP |  # With this style, tabs are drawn along the top of the notebook
                 # aui.AUI_NB_BOTTOM |              #With this style, tabs are drawn along the bottom of the notebook
                 ## aui.AUI_NB_LEFT |               #With this style, tabs are drawn along the left of the notebook. Not implemented yet.
                 ## aui.AUI_NB_RIGHT |              #With this style, tabs are drawn along the right of the notebook. Not implemented yet.
                 # aui.AUI_NB_CLOSE_BUTTON |        #With this style, a close button is available on the tab bar
                 aui.AUI_NB_CLOSE_ON_ACTIVE_TAB |  # With this style, a close button is available on the active tab
                 # aui.AUI_NB_CLOSE_ON_ALL_TABS |   #With this style, a close button is available on all tabs
                 aui.AUI_NB_SCROLL_BUTTONS |  # With this style, left and right scroll buttons are displayed
                 # aui.AUI_NB_TAB_EXTERNAL_MOVE |     #Allows a tab to be moved to another tab control
                 # aui.AUI_NB_TAB_FIXED_WIDTH |     #With this style, all tabs have the same width
                 aui.AUI_NB_TAB_MOVE |  # Allows a tab to be moved horizontally by dragging
                 aui.AUI_NB_TAB_SPLIT |  # Allows the tab control to be split by dragging a tab
                 # aui.AUI_NB_HIDE_ON_SINGLE_TAB |  #Hides the tab window if only one tab is present
                 aui.AUI_NB_SUB_NOTEBOOK |  # This style is used by AuiManager to create automatic AuiNotebooks
                 aui.AUI_NB_MIDDLE_CLICK_CLOSE |  # Allows to close AuiNotebook tabs by mouse middle button click
                 aui.AUI_NB_SMART_TABS |  # Use Smart Tabbing, like Alt + Tab on Windows
                 # aui.AUI_NB_USE_IMAGES_DROPDOWN | #Uses images on dropdown window list menu instead of check items
                 # aui.AUI_NB_CLOSE_ON_TAB_LEFT |   #Draws the tab close button on the left instead of on the right (a la Camino browser)
                 aui.AUI_NB_TAB_FLOAT |  # Allows the floating of single tabs. Known limitation: when the notebook is more or less full screen, tabs cannot be dragged far enough outside of the notebook to become floating pages
                 aui.AUI_NB_DRAW_DND_TAB |  # Draws an image representation of a tab while dragging (on by default)
                 aui.AUI_NB_ORDER_BY_ACCESS |  # Tab navigation order by last access time for the tabs
                 # aui.AUI_NB_NO_TAB_FOCUS |        #Don't draw tab focus rectangle
                 aui.AUI_NB_WINDOWLIST_BUTTON  # With this style, a drop-down list of windows is available
                 , name='auinotebook'):
        """
        Default class constructor.

        :param `parent`: Pointer to a parent window.
        :type `parent`: `wx.Window`
        :param `id`: Window identifier.
        :type `id`: int
        :param `pos`: Window position.
        :type `pos`: `wx.Point`
        :param `size`: Window size.
        :type `size`: `wx.Size`
        :param `style`: Window style.
        :type `style`: long
        :param `agwStyle`: The AGW-specific window style.
        :type `agwStyle`: int
        :param `name`: Window name.
        :type `name`: str
        """
        aui.AuiNotebook.__init__(self, parent, id, pos, size, style, agwStyle, name)


class GuiMain(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: GuiMain.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((697, 552))
        self.main_notebook = BaseAuiNotebook(self)
        self.Bind(wx.EVT_BOOKCTRL_PAGE_CHANGED, self.on_page_changed, self.main_notebook)

        # Menu Bar
        self.menubar = wx.MenuBar()
        wxglade_tmp_menu = wx.Menu()
        menu_import = wxglade_tmp_menu.Append(wx.ID_ANY, "Import", "")
        self.Bind(wx.EVT_MENU, self.on_menu_import, menu_import)

        menu_export = wxglade_tmp_menu.Append(wx.ID_ANY, "Export", "")
        self.Bind(wx.EVT_MENU, self.on_menu_export, menu_export)
        self.menubar.Append(wxglade_tmp_menu, "File")
        wxglade_tmp_menu = wx.Menu()
        menu_stitch_edit = wxglade_tmp_menu.Append(wx.ID_ANY, "Stitch Edit", "")
        self.Bind(wx.EVT_MENU, self.on_menu_stitch_edit, menu_stitch_edit)

        self.menubar.Append(wxglade_tmp_menu, "Edit")
        wxglade_tmp_menu = wx.Menu()
        menu_simulate = wxglade_tmp_menu.Append(wx.ID_ANY, "Simulate", "")
        self.Bind(wx.EVT_MENU, self.on_menu_simulate, menu_simulate)
        self.menubar.Append(wxglade_tmp_menu, "View")
        self.SetMenuBar(self.menubar)

        wxglade_tmp_menu = wx.Menu()
        menu_close = wxglade_tmp_menu.Append(wx.ID_ANY, "About", "")
        self.Bind(wx.EVT_MENU, self.on_menu_about, menu_close)
        self.menubar.Append(wxglade_tmp_menu, "Help")
        self.SetMenuBar(self.menubar)
        # Menu Bar end

        self.__set_properties()
        # self.__do_layout()
        # end wxGlade
        self.designs = []
        self.focused_design = None

        self.Bind(wx.EVT_DROP_FILES, self.on_drop_file)

    def on_menu_about(self, event):
        import embroidePyAboutDialog
        about = embroidePyAboutDialog.MyDialog()
        about.Show()

    def on_drop_file(self, event):
        for pathname in event.GetFiles():
            pattern = pyembroidery.read(str(pathname))
            pattern.extras["filename"] = pathname
            self.add_embroidery(pattern)

    def on_page_changed(self, event):
        page = self.main_notebook.CurrentPage
        if isinstance(page, ColorEmbroidery):
            self.focused_design = page.design

    def on_menu_stitch_edit(self, event):
        if self.focused_design is None:
            return
        stitch_list = StitchEditor(None, wx.ID_ANY, "")
        stitch_list.set_design(self.focused_design)
        stitch_list.Show()

    def on_menu_import(self, event):
        files = ""
        for format in pyembroidery.supported_formats():
            try:
                if format["reader"] is not None:
                    files += "*." + format["extension"] + ";"
            except KeyError:
                pass

        with wx.FileDialog(self, "Open Embroidery", wildcard="Embroidery Files (" + files + ")",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind
            pathname = fileDialog.GetPath()
            pattern = pyembroidery.read(str(pathname))
            pattern.extras["filename"] = pathname
            self.add_embroidery(pattern)

    def on_menu_export(self, event):
        files = ""
        for format in pyembroidery.supported_formats():
            try:
                if format["writer"] is not None:
                    files += format["description"] + "(*." + format["extension"] + ")|*." + format[
                        "extension"] + "|"
            except KeyError:
                pass

        with wx.FileDialog(self, "Save Embroidery", wildcard=files[:-1],
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # save the current contents in the file
            pathname = fileDialog.GetPath()
            pyembroidery.write(self.focused_design, str(pathname))

    def on_menu_simulate(self, event):
        simulator = SimulatorView(None, wx.ID_ANY, "")
        simulator.set_design(self.focused_design)
        simulator.Show()

    def add_embroidery(self, embroidery):
        self.designs.append(embroidery)
        page_sizer = wx.BoxSizer(wx.HORIZONTAL)
        embrodery_panel = ColorEmbroidery(self.main_notebook, wx.ID_ANY)
        embrodery_panel.set_design(embroidery)
        head, tail = os.path.split(embroidery.extras['filename'])
        self.main_notebook.AddPage(embrodery_panel, tail)
        page_sizer.Add(self.main_notebook, 1, wx.EXPAND, 0)
        page = self.main_notebook.GetCurrentPage()
        if isinstance(page, ColorEmbroidery):
            self.focused_design = page.design
        self.Layout()

    def __set_properties(self):
        # begin wxGlade: GuiMain.__set_properties
        self.SetTitle("EmbroidepyEditor")
        self.DragAcceptFiles(True)
        # end wxGlade


# end of class GuiMain

class Embroidepy(wx.App):
    def OnInit(self):
        self.main_editor = GuiMain(None, wx.ID_ANY, "")
        self.SetTopWindow(self.main_editor)
        self.main_editor.Show()
        return True

    def add_embroidery(self, embroidery):
        self.main_editor.add_embroidery(embroidery)

    # end of class Embroidepy


if __name__ == "__main__":
    filename = None
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    embroiderpy = Embroidepy(0)
    if filename is not None:
        emb_pattern = pyembroidery.read(filename)
        emb_pattern.extras["filename"] = filename
        embroiderpy.add_embroidery(emb_pattern)
    embroiderpy.MainLoop()
