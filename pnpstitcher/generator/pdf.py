from pnpstitcher.generator.base import BaseGenerator
import cairocffi as cairo


class PdfGenerator(BaseGenerator):
    def __init__(
            self, filename, page_width, page_height, page_margin_x=0,
            page_margin_y=0, dpi=300):
        """
        :param str filename: The filename of the output PDF file.
        :param int page_width: Page width in pixel.
        :param int page_height: Page height in pixel.
        :param int page_margin_x: The paper margin on the x-axis in pixels
                                  (both sides).
        :param int page_margin_y: The paper margin on the y-axis in pixels
                                  (both sides).
        :param int dpi: The dpi.
        """
        super(PdfGenerator, self).__init__(
            filename, page_width, page_height, page_margin_x, page_margin_y,
            dpi)

        # Cairo PDF surface uses points
        dpi_to_pp = 72 / dpi

        # Set the page and drawing context
        self._pdf = cairo.PDFSurface(
            filename, page_width * dpi_to_pp, page_height * dpi_to_pp)
        self._context = cairo.Context(self._pdf)
        self._context.scale(dpi_to_pp, dpi_to_pp)

    def _render(self, image_catalog):
        """
        Render the images on pages.

        :param ImageCatalog image_catalog: The loaded image database.
        """
        x_cnt = 0
        y_cnt = 0
        x_pos = 0
        y_pos = 0

        for pil_image in image_catalog.image_set:
            # Draw cut lines if it's a fresh page
            if x_cnt == 0 and y_cnt == 0:
                self._draw_cutlines()

            # Draw the image
            x_pos = (
                self._cut_margin_x + x_cnt * image_catalog.image_size[0] - 1)
            y_pos = (
                self._cut_margin_y + y_cnt * image_catalog.image_size[1] - 1)
            image = cairo.ImageSurface.create_from_png(pil_image.fp.name)
            self._context.set_source_surface(image, x_pos, y_pos)
            self._context.paint()

            # Switch to next row when it is happening
            x_cnt = x_cnt + 1
            if x_cnt >= self._card_num_x:
                x_cnt = 0
                y_cnt = y_cnt + 1

            # If we got past the page threshold, we would need to cease it
            if y_cnt >= self._card_num_y:
                x_cnt = 0
                y_cnt = 0
                self._pdf.show_page()

        if x_cnt != 0 or y_cnt != 0:
            self._pdf.show_page()

    def _draw_cutlines(self):
        """
        Draw cutlines.
        """
        # Set the style
        self._context.set_source_rgba(0.6, 0.6, 0.6, 1)
        self._context.set_line_width(1)
        self._context.set_dash((30, 15), 0)

        # Draw lines
        for line in self._cutline_set:
            self._context.move_to(line.x0, line.y0)
            self._context.line_to(line.x1, line.y1)

        # Paint the lines
        self._context.stroke()
