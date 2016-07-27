from pnpstitcher.generator.base import BaseGenerator
import cairocffi as cairo


class PdfGenerator(BaseGenerator):
    def __init__(self, filename, page_width, page_height, dpi):
        """
        :param str filename: The filename of the output PDF file.
        :param int page_width: Page width in pixel.
        :param int page_height: Page height in pixel.
        :param int dpi: The dpi.
        """
        dpi_to_pp = 72 / dpi

        # Set the page and drawing context
        self._pdf = cairo.PDFSurface(
            filename, page_width * dpi_to_pp, page_height * dpi_to_pp)
        self._context = cairo.Context(self._pdf)
        self._context.scale(dpi_to_pp, dpi_to_pp)

    def load_png(self, filename_set):
        """
        Load the PNG files to generate as output.

        :param list filename_set: The list of file name to be loaded.
        """
        pass

    def _draw_cutlines(self, cutline_set):
        """
        Draw cutlines.

        :param list cutline_set: The list of the cutlines.
        """
        # Set the style
        self._context.set_source_rgba(0.6, 0.6, 0.6, 1)
        self._context.set_line_width(1)
        self._context.set_dash((30, 15), 0)

        # Draw lines
        for line in cutline_set:
            self._context.move_to(line.x0, line.y0)
            self._context.line_to(line.x1, line.y1)

        # Paint the lines
        self._context.stroke()
