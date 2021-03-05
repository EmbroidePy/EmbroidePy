#!/usr/bin/env python

import wx

from embroidepy.assets import EmbroidePyLogo, texture

PHOENIX = 'phoenix' in wx.version()


class AboutWindow(wx.Window):
    def __init__(self, parent, text=''):
        ## super(AboutWindow, self).__init__(parent, style=wx.BORDER_SIMPLE)
        wx.Window.__init__(self, parent, style=wx.BORDER_SIMPLE)

        self.font = font = self.GetFont()
        self.font = font = wx.Font(42,
                                   wx.FONTFAMILY_DEFAULT,
                                   wx.FONTSTYLE_NORMAL,
                                   wx.FONTWEIGHT_NORMAL,
                                   False)
        self.SetFont(font)

        self.timer = wx.Timer(self, wx.ID_ANY)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.text = text

        self.step = 0
        self.speed = 42  # why not lol
        wx.CallAfter(self.StartTimer)

        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)

        self.bmp = EmbroidePyLogo.Bitmap
        if PHOENIX:
            self.bmpBrush = wx.Brush(texture.Bitmap)
        else:
            self.bmpBrush = wx.BrushFromBitmap(texture.Bitmap)

    def StartTimer(self, speed=None):
        """Essentially this is the speed control of the embroidery machine/logo bounce"""
        if speed:
            self.timer.Start(speed)
        else:
            self.timer.Start(self.speed)

    def OnMouseWheel(self, event):
        rotation = event.GetWheelRotation()
        if rotation < 0:
            if self.speed:  # greater than 0
                self.speed -= 1
            else:
                pass  ## wx.Bell()
        else:
            self.speed += 1
        self.StartTimer()

    def OnSize(self, event):
        self.Refresh()

    def OnEraseBackground(self, event):
        pass  # Reduce Flicker with BufferedPaint

    def OnPaint(self, event):
        sineTable = (0, 12.5, 25, 37.5, 50, 62.5, 75, 87.5,
                     100, 87.5, 75, 62.5, 50, 37.5, 25, 12.5,
                     0, -12.5, -25, -37.5, -50, -62.5, -75, -87.5,
                     -100, -87.5, -75, -62.5, -50, -37.5, -25, -12.5)

        dc = wx.BufferedPaintDC(self)
        dc.Clear()
        dc.SetBrush(self.bmpBrush)
        if PHOENIX:
            dc.DrawRectangle(self.GetClientRect())
        else:
            dc.DrawRectangleRect(self.GetClientRect())

        fnt = dc.GetFont()
        if self.text:
            text = self.text
        else:
            text = ' '
        width, height, descent, externalLeading = dc.GetFullTextExtent(text, fnt)
        cSzX, cSzY = self.GetClientSize()
        x = (cSzX - width) / 2
        y = (cSzY + externalLeading - descent) / 2
        color = wx.Colour()

        color.Set(128, 255, 128)  # Greens

        dc.SetTextForeground(wx.BLACK)
        dropShadow = 1
        dc.DrawText(text, x - dropShadow, y - ((sineTable[0] * height) / 100) - dropShadow)

        dc.SetTextForeground(color)
        dc.DrawText(text, x, y - ((sineTable[0] * height) / 100))

        step = self.step
        dc_GetFullTextExtent = dc.GetFullTextExtent
        for i, ch in enumerate(text):
            index = (step + i) % 16
            x += dc_GetFullTextExtent(ch, fnt)[0]

        needleTheo = 150
        dc.DrawBitmap(self.bmp, x - needleTheo, y - ((sineTable[index] * height) / 100) - needleTheo, useMask=True)

    def SetText(self, text):
        self.text = text

    def OnTimer(self, event):
        self.step += 1
        self.Update()
        self.Refresh()


class MyDialog(wx.Dialog):
    def __init__(self, parent=None, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER):
        wx.Dialog.__init__(self, parent, style=style)

        self.aboutWin = AboutWindow(self)
        self.aboutWin.SetText('EmbroidePy')

        vbSizer = wx.BoxSizer(wx.VERTICAL)
        vbSizer.Add(self.aboutWin, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(vbSizer)

        self.SetTitle("About EmbroidePy")
        self.SetSize((512, 512))

        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnText(self, event):
        self.aboutWin.SetText(event.GetString())

    def OnClose(self, event):
        self.aboutWin.timer.Stop()
        self.Destroy()


if __name__ == '__main__':
    app = wx.App(0)
    dialog = MyDialog(None)
    dialog.Show()
    app.MainLoop()
