# EmbroidePy
Embroidery Tools

`pip install pyembroidery`

If the utility has a GUI and requires wxPython:

`pip install wxPython`

---

* embroidepy.py	GUI - interface embroidery editor.
   * Uses wxPython and pyembroidery to import, export, view multiple files. Simulates sew paths, forwards and backwards.
   * Has a wxGrid based stitch editor to allow on the fly stitch editing of designs.
* MaKe-stitch.py GUI - for making .pmv stitch files (or other ones, but there aren't any other ones).
   * ![make-stitch](https://user-images.githubusercontent.com/3302478/44017845-9e4cb12e-9e8e-11e8-9849-f9b9ba75d516.png)
   * Double-Click adds points.
   * Click selects nodes.
   * Drag selected nodes to new locations.
   * (In Windows) You can drag-and-drop files (other OS's when wxPython supports with the bind I used).
   * Right-click nodes, for popup menu.
   * Delete button deletes selected node.
   * Right Arrow and 'd' moves to the next node in the list.
   * Left Arrow and 'a' moves to the next node in the list. ('a' & 'd' are WASD keys).
* mass_convert.py	CLI - Converts every file in directory `./convert` to `./results` for every acceptable filetype and into every acceptable result.
* pyembroidery-convert.py	CLI - (Source File) (Destination File) convert an embroidery file from one type to another. By default makes .csv files.
* pyembroidery-exporter.py  CLI - (Source File) - Converts an embroidery file from some type to `.u01, .exp, .dst, .jef, .pes, .vp3`
* stitch_entry_pmv.py CLI - Text interface - Allows creating stitch files from a purely text base interface expecting values between [0,14] and [-30,30]

The stitch_entry_pmv script works but the MaKe-stitch program is a fully realized GUI.
