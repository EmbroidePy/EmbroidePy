# EmbroidePy
Embroidery Tools

`pip install pyembroidery`

If the utility has a GUI and requires wxPython:

`pip install wxPython`

---

* embroidepy.py	GUI - interface embroidery editor.
   * ![embroidepy](https://user-images.githubusercontent.com/3302478/44623722-06096680-a88b-11e8-8e7d-30b210892ba1.png)
   * Uses wxPython and pyembroidery to import, export, view multiple files.
   * Simulates sew paths, forwards and backwards.
      * ![empy-sim](https://user-images.githubusercontent.com/3302478/44623750-ef174400-a88b-11e8-9fdc-dfb2cebefc41.png)
   * Has a wxGrid based stitch editor to allow on the fly stitch editing of designs.
   * Allows drag and drop of individual stitches.
   * Allows zoom-in zoom-out and pan on the fly.
   * Keyboard Commands:
      * 'q' injects stitches.
      * Delete button deletes selected node.
      * Right Arrow or 'd' moves to the next node in the list.
      * Left Arrow or 'a' moves to the next node in the list. ('a' & 'd' are WASD keys).
      * Escape deselects selected node.
* MaKe-stitch.py GUI - for making .pmv stitch files (or other ones, but there aren't any other ones).
   * ![make-stitch](https://user-images.githubusercontent.com/3302478/44017845-9e4cb12e-9e8e-11e8-9849-f9b9ba75d516.png)
   * See tutorial video: https://youtu.be/HCiFgb9-JHQ
   * Left Double-Click inserts a stitch.
   * Middle Double-Click inserts a stitch. Note: Since Left Click selects a node, double clicking a node selects then inserts at that exact location which duplicates the node. Using middle click means it will allow double-backing on nodes without selecting them.
   * Right Double-Click inserts a triple stitch.
   * Left Click selects nodes.
   * Right-click: on nodes, opens popup menu (delete, duplicate).
   * Drag-and-Move selected nodes to new locations.
   * (In Windows) Drag-and-drop files to open them (other OS's when wxPython supports with the bind I used).
   * Keyboard Commands:
      * Delete button deletes selected node.
      * Right Arrow or 'd' moves to the next node in the list.
      * Left Arrow or 'a' moves to the next node in the list. ('a' & 'd' are WASD keys).
* mass_convert.py	CLI - Converts every file in directory `./convert` to `./results` for every acceptable filetype and into every acceptable result.
* pyembroidery-convert.py	CLI - (Source File) (Destination File) convert an embroidery file from one type to another. By default makes .csv files.
* pyembroidery-exporter.py  CLI - (Source File) - Converts an embroidery file from some type to `.u01, .exp, .dst, .jef, .pes, .vp3`
* stitch_entry_pmv.py CLI - Text interface - Allows creating stitch files from a purely text base interface expecting values between [0,14] and [-30,30]

The stitch_entry_pmv script works but the MaKe-stitch program is a fully realized GUI.
