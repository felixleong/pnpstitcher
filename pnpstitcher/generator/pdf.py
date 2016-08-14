from pnpstitcher.generator.base import BaseGenerator
import cairocffi as cairo


class PdfGenerator(BaseGenerator):
    def __init__(
            self, filename, page_width, page_height, page_margin_x=0,
            page_margin_y=0, image_dpi=300, page_dpi=96):
        """
        :param str filename: The filename of the output PDF file.
        :param int page_width: Page width in pixel.
        :param int page_height: Page height in pixel.
        :param int page_margin_x: The paper margin on the x-axis in pixels
                                  (both sides).
        :param int page_margin_y: The paper margin on the y-axis in pixels
                                  (both sides).
        :param int image_dpi: The image dpi.
        :param int page_dpi: The page dpi.
        """
        super(PdfGenerator, self).__init__(
            filename, page_width, page_height, page_margin_x, page_margin_y,
            image_dpi, page_dpi)

        # Set the page and drawing context
        self._pdf = cairo.PDFSurface(
            filename, page_width * 72, page_height * 72)
        self._context = cairo.Context(self._pdf)

    def _draw_image(self, pil_image, x_pos, y_pos, image_dimension):
        """
        Draw image onto page.

        :param Image pil_image: The image.
        :param int x_pos: The x position in pixel.
        :param int y_pos: The y position in pixel.
        :param list image_dimension: A 2-tuple containing the image width and
            height.
        """
        self._context.save()
        image = cairo.ImageSurface.create_from_png(pil_image.fp.name)
        self._context.scale(self.image_scale, self.image_scale)
        self._context.set_source_surface(
            image, x_pos * self.image_dpi, y_pos * self.image_dpi)
        self._context.paint()
        self._context.restore()

    def _initialize_page(self):
        """
        Start a fresh page.
        """
        return

    def _render_page(self):
        """
        Render page.
        """
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
            self._context.set_dash((4, 4), 0)

        # Draw lines
        for line in self._cutline_set:
            self._context.move_to(
                line.x0 * self.page_dpi, line.y0 * self.page_dpi)
            self._context.line_to(
                line.x1 * self.page_dpi, line.y1 * self.page_dpi)

        # Paint the lines
        self._context.stroke()
