# -wxPython Imports.
import wx

from .embroideryview import EmbroideryView


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
