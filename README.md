# EmbroidePy
Embroidery Tools

`pip install pyembroidery`

If the utility has a GUI and requires wxPython:

`pip install wxPython`

---

* embroidepy.py	GUI - interface embroidery editor.
   * ![embroiderpy](https://user-images.githubusercontent.com/3302478/44672208-a0c58a80-a9dc-11e8-8119-fbacdd7f1050.png)
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
