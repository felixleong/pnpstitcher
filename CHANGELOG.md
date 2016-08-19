# 0.2

- SVG generation support *(assuming raster card images, haven't tried out w/
  SVG vector images yet -- would assume that it won't work right)*
- Several image generation modes:
    - `full`: To include both cutline and images
    - `cutline`: Just the cutlines
    - `image`: Just the images
- Two new styles of cutlines:
    - `cutthrough`: to draw cut-through lines at the margins, best used w/
      manual cutters by hand.
    - `inset`: to draw a cutline around the cards, which would be useful if you
      use a die-cutting machine.
- Draws one registration mark for calibration purposes.

# 0.1

Initial release of PNP Stitcher, which includes the following two configurable scripts:

- `pnpstitch.py`: Stitch a group of PNG files that have the same dimension into
  sheets of pages together with cut lines along the margins.
- `pnpduplex.py`: Combine two PDF files into a single duplex PDF file for use
  in duplex printers.
