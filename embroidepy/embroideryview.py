import sys

# -pyembroidery Imports.
import pyembroidery
# -wxPython Imports.
import wx
import wx.grid
from pyembroidery.CsvWriter import get_common_name_dictionary
from pyembroidery.EmbConstant import *
from pyembroidery.EmbThread import EmbThread

from .zoomerpanel import ZoomerPanel

STATIC_COLOR_LIST = (
    0x000000, 0x00FF00, 0x0000FF, 0xFF0000, 0x01FFFE, 0xFFA6FE, 0xFFDB66, 0x006401, 0x010067, 0x95003A, 0x007DB5,
    0xFF00F6, 0xFFEEE8, 0x774D00, 0x90FB92, 0x0076FF, 0xD5FF00, 0xFF937E, 0x6A826C, 0xFF029D, 0xFE8900, 0x7A4782,
    0x7E2DD2, 0x85A900, 0xFF0056, 0xA42400, 0x00AE7E, 0x683D3B, 0xBDC6FF, 0x263400, 0xBDD393, 0x00B917, 0x9E008E)


class EmbroideryView(ZoomerPanel):
    def __init__(self, *args, **kwds):
        self.draw_data = None
        self.emb_pattern = None
        self.buffer = 0.05
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
        self.paint_count = 0

        self.on_size(None)

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
        if self.clicked_position[0] != self.clicked_position[0]:  # NaN check
            self.focus_position_scene((0, 0))
            self.clicked_position = self.convert_window_to_scene(event.GetPosition())

        nearest = self.get_nearest_point(self.clicked_position)
        if nearest[0] is None:  # No nearest means there's no points.
            position = self.clicked_position
            stitches = self.emb_pattern.stitches
            stitches.append([float(position[0]), float(position[1]), pyembroidery.STITCH])
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
                self.focus_position_scene(stitch)

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
                self.focus_position_scene(stitch)

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
                self.focus_position_scene(stitch)
            self.draw_data = None
            self.update_drawing()
        elif keycode in [32]:
            if self.selected_point is None:
                return
            stitches = self.emb_pattern.stitches
            stitch = stitches[self.selected_point]
            self.focus_position_scene(stitch)
            self.update_drawing()

    def create_draw_data(self):
        stitches = self.emb_pattern.stitches
        draw_data = []
        color_index = 0
        try:
            color = self.emb_pattern.get_thread(color_index)
        except IndexError:
            color = EmbThread()
            color.set(STATIC_COLOR_LIST[color_index % len(STATIC_COLOR_LIST)])
        color_index += 1
        lines = []
        trimmed = True
        command = NO_COMMAND

        i = -1
        ie = len(stitches) - 2
        while i < ie:
            i += 1
            current_stitch = stitches[i]
            next_stitch = stitches[i + 1]
            lines.append([current_stitch[0], current_stitch[1], next_stitch[0], next_stitch[1]])
            command = current_stitch[2] & COMMAND_MASK
            if command == COLOR_CHANGE or command == NEEDLE_SET:
                try:
                    color = self.emb_pattern.get_thread(color_index)
                except IndexError:
                    color = EmbThread()
                    color.set(STATIC_COLOR_LIST[color_index % len(STATIC_COLOR_LIST)])
                color_index += 1
            if command == next_stitch[2]:
                continue
            if command == STITCH or command == SEQUIN_EJECT or command == SEW_TO or command == NEEDLE_AT:
                trimmed = False
            elif command == TRIM or command == COLOR_CHANGE or \
                    command == COLOR_BREAK or command == SEQUENCE_BREAK or \
                    command == NEEDLE_SET:
                trimmed = True
            color_tuple = (color.get_red(), color.get_green(), color.get_blue())
            draw_data.append((
                color_tuple,
                lines,
                command,
                trimmed))
            lines = []

        if len(lines) > 0:
            color_tuple = (color.get_red(), color.get_green(), color.get_blue())
            draw_data.append((
                (color_tuple),
                lines,
                command,
                trimmed))
        return draw_data

    def on_draw_background(self, dc):
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
        # scale_bit = math.pow(self.get_scale_x(), -0.6)
        scale_bit = 1

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

    def update_affine(self):
        if self.emb_pattern is None:
            return
        extends = self.emb_pattern.bounds()
        # self.focus_viewport_scene(extends, self.buffer, False) # Makes scale unlocked
        self.focus_viewport_scene(extends, self.buffer)
        self.update_drawing()

    def on_size(self, event):
        ZoomerPanel.on_size(self, event)
        self.draw_data = None
        self.update_affine()

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
        best_distance = float('inf')
        for i, stitch in enumerate(self.emb_pattern.stitches):
            distance = self.distance_sq(position, stitch)
            if best_point is None or distance < best_distance or (
                    distance == best_distance and self.selected_point == i):
                best_point = stitch
                best_distance = distance
                best_index = i
        return best_index, best_distance, best_point

# end of class EmbroideryView
