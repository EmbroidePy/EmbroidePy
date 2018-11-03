#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

# Imports.--------------------------------------------------------------------
# -Python Imports.
import os
import sys

# -pyembroidery Imports.
import pyembroidery
# -wxPython Imports.
import wx
import wx.grid
import wx.lib.agw.aui as aui
from EmbroideryView import EmbroideryView
from SimulatorView import SimulatorView
from StatisticsView import StatisticsView
from StitchEditor import StitchEditor


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

        # Menu Bar
        self.menubar = wx.MenuBar()
        wxglade_tmp_menu = wx.Menu()
        menu_new = wxglade_tmp_menu.Append(wx.ID_ANY, "New", "")
        menu_save = wxglade_tmp_menu.Append(wx.ID_ANY, "Save", "")
        menu_save_as = wxglade_tmp_menu.Append(wx.ID_ANY, "Save As", "")
        menu_export = wxglade_tmp_menu.Append(wx.ID_ANY, "Export", "")
        menu_import = wxglade_tmp_menu.Append(wx.ID_ANY, "Import", "")
        wxglade_tmp_menu.AppendSeparator()
        wxglade_tmp_menu_sub = wx.Menu()
        menu_print = wxglade_tmp_menu_sub.Append(wx.ID_ANY, "Print", "")
        menu_print_preview = wxglade_tmp_menu_sub.Append(wx.ID_ANY, "Print Preview", "")
        menu_print_setup = wxglade_tmp_menu_sub.Append(wx.ID_ANY, "Print Setup", "")
        wxglade_tmp_menu.Append(wx.ID_ANY, "Print", wxglade_tmp_menu_sub, "")
        wxglade_tmp_menu.AppendSeparator()
        wxglade_tmp_menu.Append(wx.ID_ANY, "Exit", "")
        self.menubar.Append(wxglade_tmp_menu, "File")
        wxglade_tmp_menu = wx.Menu()
        menu_stitch_edit = wxglade_tmp_menu.Append(wx.ID_ANY, "Stitch Edit", "")
        menu_undo = wxglade_tmp_menu.Append(wx.ID_ANY, "Undo", "")
        menu_redo = wxglade_tmp_menu.Append(wx.ID_ANY, "Redo", "")
        wxglade_tmp_menu.AppendSeparator()
        wxglade_tmp_menu_sub = wx.Menu()
        menu_reduce = wxglade_tmp_menu_sub.Append(wx.ID_ANY, "Reduce", "")
        menu_enlarge = wxglade_tmp_menu_sub.Append(wx.ID_ANY, "Enlarge", "")
        menu_rotate_cw = wxglade_tmp_menu_sub.Append(wx.ID_ANY, u"Rotate \u03c4/4", "")
        menu_rotate_ccw = wxglade_tmp_menu_sub.Append(wx.ID_ANY, u"Rotate -\u03c4/4", "")
        menu_horizontal_flip = wxglade_tmp_menu_sub.Append(wx.ID_ANY, "H-Flip", "")
        menu_vertical_flip = wxglade_tmp_menu_sub.Append(wx.ID_ANY, "V-Flip", "")
        wxglade_tmp_menu.Append(wx.ID_ANY, "Transform", wxglade_tmp_menu_sub, "")
        wxglade_tmp_menu.AppendSeparator()
        menu_points_mode = wxglade_tmp_menu.Append(wx.ID_ANY, "Points Mode", "", wx.ITEM_RADIO)
        menu_lines_mode = wxglade_tmp_menu.Append(wx.ID_ANY, "Lines Mode", "", wx.ITEM_RADIO)
        wxglade_tmp_menu.AppendSeparator()
        menu_select_mode = wxglade_tmp_menu.Append(wx.ID_ANY, "Select Mode", "", wx.ITEM_RADIO)
        menu_move_mode = wxglade_tmp_menu.Append(wx.ID_ANY, "Move Mode", "", wx.ITEM_RADIO)
        menu_insert_mode = wxglade_tmp_menu.Append(wx.ID_ANY, "Insert Mode", "", wx.ITEM_RADIO)
        wxglade_tmp_menu.AppendSeparator()
        self.menubar.Append(wxglade_tmp_menu, "Edit")
        wxglade_tmp_menu = wx.Menu()
        menu_simulate = wxglade_tmp_menu.Append(wx.ID_ANY, "Simulate", "")
        menu_show_grid = wxglade_tmp_menu.Append(wx.ID_ANY, "Show Grid", "", wx.ITEM_CHECK)
        menu_show_guides = wxglade_tmp_menu.Append(wx.ID_ANY, "Show Guides", "", wx.ITEM_CHECK)
        menu_show_jumps = wxglade_tmp_menu.Append(wx.ID_ANY, "Show Jump Stitches", "", wx.ITEM_CHECK)
        menu_show_functions = wxglade_tmp_menu.Append(wx.ID_ANY, "Show Functions", "", wx.ITEM_CHECK)
        self.menubar.Append(wxglade_tmp_menu, "View")
        wxglade_tmp_menu = wx.Menu()
        menu_statistics = wxglade_tmp_menu.Append(wx.ID_ANY, "Statistics", "")
        menu_small_stitches = wxglade_tmp_menu.Append(wx.ID_ANY, "Remove Small Stitches", "")
        self.menubar.Append(wxglade_tmp_menu, "Design")
        wxglade_tmp_menu = wx.Menu()
        menu_about = wxglade_tmp_menu.Append(wx.ID_ANY, "About", "")
        self.menubar.Append(wxglade_tmp_menu, "Help")
        self.SetMenuBar(self.menubar)
        # Menu Bar end
        self.Bind(wx.EVT_MENU, self.on_menu_new, menu_new)
        self.Bind(wx.EVT_MENU, self.on_menu_save, menu_save)
        self.Bind(wx.EVT_MENU, self.on_menu_save_as, menu_save_as)
        self.Bind(wx.EVT_MENU, self.on_menu_print, menu_print)
        self.Bind(wx.EVT_MENU, self.on_menu_print_preview, menu_print_preview)
        self.Bind(wx.EVT_MENU, self.on_menu_print_setup, menu_print_setup)
        self.Bind(wx.EVT_MENU, self.on_menu_undo, menu_undo)
        self.Bind(wx.EVT_MENU, self.on_menu_redo, menu_redo)
        self.Bind(wx.EVT_MENU, self.on_menu_reduce, menu_reduce)
        self.Bind(wx.EVT_MENU, self.on_menu_enlarge, menu_enlarge)
        self.Bind(wx.EVT_MENU, self.on_menu_rotate_cw, menu_rotate_cw)
        self.Bind(wx.EVT_MENU, self.on_menu_rotate_ccw, menu_rotate_ccw)
        self.Bind(wx.EVT_MENU, self.on_menu_horizontal_flip, menu_horizontal_flip)
        self.Bind(wx.EVT_MENU, self.on_menu_vertical_flip, menu_vertical_flip)

        self.Bind(wx.EVT_MENU, self.on_menu_points_mode, menu_points_mode)
        self.Bind(wx.EVT_MENU, self.on_menu_lines_mode, menu_lines_mode)

        self.Bind(wx.EVT_MENU, self.on_menu_select_mode, menu_select_mode)
        self.Bind(wx.EVT_MENU, self.on_menu_insert_mode, menu_insert_mode)
        self.Bind(wx.EVT_MENU, self.on_menu_move_mode, menu_move_mode)

        self.Bind(wx.EVT_MENU, self.on_menu_import, menu_import)
        self.Bind(wx.EVT_MENU, self.on_menu_export, menu_export)
        self.Bind(wx.EVT_MENU, self.on_menu_stitch_edit, menu_stitch_edit)
        self.Bind(wx.EVT_MENU, self.on_menu_simulate, menu_simulate)

        self.Bind(wx.EVT_MENU, self.on_menu_show_grid, menu_show_grid)
        self.Bind(wx.EVT_MENU, self.on_menu_show_guides, menu_show_guides)
        self.Bind(wx.EVT_MENU, self.on_menu_show_jumps, menu_show_jumps)
        self.Bind(wx.EVT_MENU, self.on_menu_show_functions, menu_show_functions)

        self.Bind(wx.EVT_MENU, self.on_menu_statistics, menu_statistics)

        self.Bind(wx.EVT_MENU, self.on_menu_small_stitches, menu_small_stitches)

        self.Bind(wx.EVT_MENU, self.on_menu_about, menu_about)
        # Menu Bar Bind end

        self.__set_properties()
        # self.__do_layout()
        # end wxGlade

        self.Bind(wx.EVT_DROP_FILES, self.on_drop_file)

    def on_menu_print(self, event):
        pass

    def on_menu_print_preview(self, event):
        pass

    def on_menu_print_setup(self, event):
        pass

    def on_menu_undo(self, event):
        pass

    def on_menu_redo(self, event):
        pass

    def on_menu_reduce(self, event):
        page = self.main_notebook.GetCurrentPage()
        if not isinstance(page, EmbroideryView) or page.emb_pattern is None:
            return
        pattern = page.emb_pattern
        m = pyembroidery.EmbMatrix()
        m.post_scale(0.9, 0.9)
        pattern.transform(m)
        page.on_size(None)
        page.update_drawing()

    def on_menu_enlarge(self, event):
        page = self.main_notebook.GetCurrentPage()
        if not isinstance(page, EmbroideryView) or page.emb_pattern is None:
            return
        pattern = page.emb_pattern
        m = pyembroidery.EmbMatrix()
        m.post_scale(1.1, 1.1)
        pattern.transform(m)
        page.on_size(None)

    def on_menu_rotate_cw(self, event):
        page = self.main_notebook.GetCurrentPage()
        if not isinstance(page, EmbroideryView) or page.emb_pattern is None:
            return
        pattern = page.emb_pattern
        m = pyembroidery.EmbMatrix()
        m.post_rotate(90)
        pattern.transform(m)
        page.on_size(None)

    def on_menu_rotate_ccw(self, event):
        page = self.main_notebook.GetCurrentPage()
        if not isinstance(page, EmbroideryView) or page.emb_pattern is None:
            return
        pattern = page.emb_pattern
        m = pyembroidery.EmbMatrix()
        m.post_rotate(-90)
        pattern.transform(m)
        page.on_size(None)

    def on_menu_horizontal_flip(self, event):
        page = self.main_notebook.GetCurrentPage()
        if not isinstance(page, EmbroideryView) or page.emb_pattern is None:
            return
        pattern = page.emb_pattern
        m = pyembroidery.EmbMatrix()
        m.post_scale(-1, 1)
        pattern.transform(m)
        page.on_size(None)

    def on_menu_vertical_flip(self, event):
        page = self.main_notebook.GetCurrentPage()
        if not isinstance(page, EmbroideryView) or page.emb_pattern is None:
            return
        pattern = page.emb_pattern
        m = pyembroidery.EmbMatrix()
        m.post_scale(1, -1)
        pattern.transform(m)
        page.on_size(None)

    def on_menu_points_mode(self, event):
        pass

    def on_menu_lines_mode(self, event):
        pass

    def on_menu_select_mode(self, event):
        pass

    def on_menu_insert_mode(self, event):
        pass

    def on_menu_move_mode(self, event):
        pass

    def on_menu_show_grid(self, event):
        pass

    def on_menu_show_guides(self, event):
        pass

    def on_menu_show_jumps(self, event):
        pass

    def on_menu_show_functions(self, event):
        pass

    def on_menu_statistics(self, event):
        page = self.main_notebook.GetCurrentPage()
        if not isinstance(page, EmbroideryView) or page.emb_pattern is None:
            return
        statistics = StatisticsView(None, wx.ID_ANY, "")
        statistics.set_design(page.emb_pattern)
        statistics.Show()

    def on_menu_small_stitches(self, event):
        pass

    def on_menu_about(self, event):
        import embroidePyAboutDialog
        about = embroidePyAboutDialog.MyDialog()
        about.Show()

    def on_menu_stitch_edit(self, event):
        page = self.main_notebook.GetCurrentPage()
        if not isinstance(page, EmbroideryView) or page.emb_pattern is None:
            return
        stitch_list = StitchEditor(None, wx.ID_ANY, "")
        stitch_list.set_design(page.emb_pattern)
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
            self.read_file(pathname)

    def on_menu_new(self, event):
        pattern = pyembroidery.EmbPattern()
        pattern.extras["filename"] = "unnamed"
        self.add_embroidery(pattern)

    def on_menu_save_as(self, event):
        page = self.main_notebook.GetCurrentPage()
        if not isinstance(page, EmbroideryView) or page.emb_pattern is None:
            return
        files = "Comma-separated values, csv (*.csv)|*.csv"
        with wx.FileDialog(self, "Save Embroidery", wildcard=files,
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind
            # save the current contents in the file
            pathname = fileDialog.GetPath()
            pyembroidery.write(page.emb_pattern, str(pathname))
            page.emb_pattern.extras["filename"] = pathname

    def on_menu_save(self, event):
        page = self.main_notebook.GetCurrentPage()
        if not isinstance(page, EmbroideryView) or page.emb_pattern is None:
            return
        path = page.emb_pattern.extras["filename"]
        if path is None:
            return
        pyembroidery.write(page.emb_pattern, str(path))

    def on_menu_export(self, event):
        page = self.main_notebook.GetCurrentPage()
        if not isinstance(page, EmbroideryView) or page.emb_pattern is None:
            return
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
            pyembroidery.write(page.emb_pattern, str(pathname))

    def on_menu_simulate(self, event):
        page = self.main_notebook.GetCurrentPage()
        if not isinstance(page, EmbroideryView) or page.emb_pattern is None:
            return
        simulator = SimulatorView(None, wx.ID_ANY, "")
        simulator.set_design(page.emb_pattern)
        simulator.Show()

    def read_file(self, filepath):
        if filepath is None:
            return
        pattern = pyembroidery.read(str(filepath))
        if pattern is None:
            return
        pattern.extras["filename"] = filepath
        self.add_embroidery(pattern)

    def on_drop_file(self, event):
        for pathname in event.GetFiles():
            self.read_file(pathname)

    def add_embroidery(self, embroidery):
        page_sizer = wx.BoxSizer(wx.HORIZONTAL)
        embroidery_panel = EmbroideryView(self.main_notebook, wx.ID_ANY)
        embroidery_panel.set_design(embroidery)
        head, tail = os.path.split(embroidery.extras['filename'])
        self.main_notebook.AddPage(embroidery_panel, tail)
        page_sizer.Add(self.main_notebook, 1, wx.EXPAND, 0)
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

    def read_file(self, filename):
        self.main_editor.read_file(filename)

    # end of class Embroidepy


if __name__ == "__main__":
    filename = None
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    embroiderpy = Embroidepy(0)
    embroiderpy.read_file(filename)
    embroiderpy.MainLoop()
