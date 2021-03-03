#!/usr/bin/env python
# -*- coding: utf-8 -*-


import wx
from zoomerpanel import ZoomerPanel


class GraphicsView(ZoomerPanel):
    def __init__(self, *args, **kwds):
        ZoomerPanel.__init__(self, *args, **kwds)

        self.zoom = '100%'

    def on_draw_background(self, dc):
        dc.SetBackground(wx.Brush("Grey"))
        dc.Clear()
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.SetPen(wx.Pen(wx.BLACK))

        width, height = self.GetClientSize()
        bmpBrush = wx.Brush(wx.Bitmap('texture.png', wx.BITMAP_TYPE_ANY))
        dc.SetBrush(bmpBrush)
        dc.DrawRectangle(-1, -1, width + 2, height + 2)
        dc.DrawRectangle(self.GetClientRect())

        dc.SetBrush(wx.Brush(wx.BLACK, style=wx.BRUSHSTYLE_CROSS_HATCH))
        dc.DrawRectangle(-1, -1, width + 2, height + 2)

    def on_draw_scene(self, dc):
        dc.SetPen(wx.Pen(wx.BLACK))
        dc.DrawBitmap(wx.Bitmap('EmbroidePyLogo.png', wx.BITMAP_TYPE_ANY), 4, 4, useMask=False)
        dc.DrawSpline(x1=100, y1=100, x2=200, y2=116, x3=200, y3=200)

    def on_draw_interface(self, dc):
        gc = wx.GraphicsContext.Create(dc)

        dc.SetPen(wx.Pen(wx.BLACK, 3))
        text = 'ZoomerPanel Demo'
        fnt = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        dc.SetFont(fnt)
        width, height, descent, externalLeading = dc.GetFullTextExtent(text)
        gc.SetBrush(wx.Brush(wx.Colour(128, 128, 128, 224)))
        border = 5
        gc.SetPen(wx.Pen(wx.Colour(0, 0, 0, 192), 3))
        gc.DrawRectangle(10 - border, 10 - border/2, width + border*2, height + border)
        gc.SetFont(fnt, wx.Colour(0, 0, 0, 255))
        gc.DrawText(text, 10, 10)

        gc.SetFont(fnt, wx.Colour(0, 0, 0, 255))
        gc.DrawText(self.zoom, 10, 50)

        print('scale x', self.get_scale_x())
        print('scale y', self.get_scale_y())


class MyFrame(wx.Frame):
    def __init__(self, parent, id=wx.ID_ANY, title=wx.EmptyString,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.DEFAULT_FRAME_STYLE, name='frame'):
        wx.Frame.__init__(self, parent, id, title, pos, size, style, name)
        global gMainWin
        gMainWin = self
        wxVER = 'wxPython %s' % wx.version()
        pyVER = 'python %d.%d.%d.%s' % sys.version_info[0:4]
        versionInfos = '%s %s' % (wxVER, pyVER)
        self.CreateStatusBar().SetStatusText(versionInfos)
        panel = GraphicsView(self)
        self.Bind(wx.EVT_CLOSE, self.OnDestroy)

    def OnDestroy(self, event):
        self.Destroy()

class MyApp(wx.App):
    def OnInit(self):
        gMainWin = MyFrame(None, size=(512, 512))
        gMainWin.SetTitle('ZoomerPanel Demo')
        self.SetTopWindow(gMainWin)
        gMainWin.Center()
        gMainWin.Show()
        return True

if __name__ == '__main__':
    import sys
    gApp = MyApp(redirect=False,
            filename=None,
            useBestVisual=False,
            clearSigInt=True)
    gApp.MainLoop()
