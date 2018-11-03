import pyembroidery
import wx


class StatisticsView(wx.Frame):
    def __init__(self, *args, **kwds):
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((845, 605))

        self.list_control = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES)
        self.__set_properties()
        self.__do_layout()
        self.pattern = None
        # end wxGlade

    def __set_properties(self):
        self.SetTitle("Statistics")
        self.list_control.AppendColumn("Statistic", format=wx.LIST_FORMAT_LEFT, width=200)
        self.list_control.AppendColumn("Value", format=wx.LIST_FORMAT_RIGHT, width=200)
        # end wxGlade

    def __do_layout(self):
        self.Layout()

    def set_design(self, pattern):
        self.pattern = pattern
        ctrl = self.list_control
        names = pyembroidery.get_common_name_dictionary()
        bounds = [float(e) / 10.0 for e in pattern.bounds()]  # convert to mm.
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        index = 0
        ctrl.SetItem(ctrl.InsertItem(index, "Command Count:"), 1, str(pattern.count_stitches()))
        index += 1
        ctrl.SetItem(ctrl.InsertItem(index, "Thread Count:"), 1, str(pattern.count_color_changes()))
        index += 1
        ctrl.SetItem(ctrl.InsertItem(index, "Needle Count:"), 1, str(pattern.count_needle_sets()))
        index += 1
        ctrl.SetItem(ctrl.InsertItem(index, "Width:"), 1, "%.1fmm" % width)
        index += 1
        ctrl.SetItem(ctrl.InsertItem(index, "Height:"), 1, "%.1fmm" % height)
        index += 1
        ctrl.SetItem(ctrl.InsertItem(index, "Left:"), 1, "%.1fmm" % bounds[0])
        index += 1
        ctrl.SetItem(ctrl.InsertItem(index, "Top:"), 1, "%.1fmm" % bounds[1])
        index += 1
        ctrl.SetItem(ctrl.InsertItem(index, "Right:"), 1, "%.1fmm" % bounds[2])
        index += 1
        ctrl.SetItem(ctrl.InsertItem(index, "Bottom:"), 1, "%.1fmm" % bounds[3])
        index += 1

        stitch_counts = {}
        for s in pattern.stitches:
            command = s[2] & pyembroidery.COMMAND_MASK
            if command in stitch_counts:
                stitch_counts[command] += 1
            else:
                stitch_counts[command] = 1

        if len(stitch_counts) != 0:
            for the_key, the_value in stitch_counts.items():
                try:
                    the_key &= pyembroidery.COMMAND_MASK
                    name = "COMMAND_" + names[the_key]
                except (IndexError, KeyError):
                    name = "COMMAND_UNKNOWN_" + str(the_key)
                ctrl.SetItem(ctrl.InsertItem(index, name), 1, "%d" % the_value)
                index += 1
        ctrl.SetItem(ctrl.InsertItem(index, "Metadata:"), 1, "%d" % len(pattern.extras))
        index += 1
        for the_key, the_value in pattern.extras.items():
            ctrl.SetItem(ctrl.InsertItem(index, "@%s" % str(the_key)), 1, str(the_value))
            index += 1
