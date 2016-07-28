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

    def _render(self, image_catalog, cutline_config):
        """
        Render the images on pages.

        :param ImageCatalog image_catalog: The loaded image database.
        :param dict cutline_config: The cutline configuration.
        """
        x_cnt = 0
        y_cnt = 0
        x_pos = 0
        y_pos = 0

        for pil_image in image_catalog.image_set:
            # Draw cut lines if it's a fresh page
            if (
                    cutline_config['layer'] == 'bottom' and
                    x_cnt == 0 and y_cnt == 0):
                self._draw_cutlines(cutline_config)

            # Draw the image
            x_pos = (
                self._cut_margin_x + x_cnt * image_catalog.image_size[0])
            y_pos = (
                self._cut_margin_y + y_cnt * image_catalog.image_size[1])
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
                if cutline_config['layer'] == 'top':
                    self._draw_cutlines(cutline_config)
                self._pdf.show_page()

        # After we hit the last page and if there's some left-over that is not
        # rendered, we should do it now.
        if x_cnt != 0 or y_cnt != 0:
            if cutline_config['layer'] == 'top':
                self._draw_cutlines(cutline_config)
            self._pdf.show_page()

    def _draw_cutlines(self, cutline_config):
        """
        Draw cutlines.

        :param dict cutline_config: The cutline configuration.
        """
        # Set the style
        self._context.set_source_rgba(*cutline_config['color'])
        self._context.set_line_width(cutline_config['width'])
        if cutline_config['dashed']:
            self._context.set_dash((7.5, 7.5), 0)

        # Draw lines
        for line in self._cutline_set:
            self._context.move_to(line.x0, line.y0)
            self._context.line_to(line.x1, line.y1)

        # Paint the lines
        self._context.stroke()
