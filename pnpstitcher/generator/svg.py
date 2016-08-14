from PIL import Image
from pnpstitcher.generator.base import BaseGenerator
import base64
import svgwrite
import os.path


class SvgGenerator(BaseGenerator):
    STYLESHEET = """
        .cutline {{
            fill: none;
            stroke: {color};
            stroke-width: {width};
            stroke-linecap: butt;
            stroke-linejoin: miter;
            stroke-opacity: 1;
            stroke-dasharray: 6, 6;
        }}
    """

    def __init__(
            self, filename, page_width, page_height, page_margin_x=0,
            page_margin_y=0, image_dpi=300, page_dpi=96):
        """
        :param str filename: The filename of the output PDF file.
        :param int page_width: Page width in inches.
        :param int page_height: Page height in inches.
        :param int page_margin_x: The paper margin on the x-axis in inches
                                  (both sides).
        :param int page_margin_y: The paper margin on the y-axis in inches
                                  (both sides).
        :param int image_dpi: The image dpi.
        :param int page_dpi: The page dpi.
        """
        super(SvgGenerator, self).__init__(
            filename, page_width, page_height, page_margin_x, page_margin_y,
            image_dpi, page_dpi)
        self.base_filename, self.ext = os.path.splitext(filename)
        self._page_number = 1
        self._drawing = None

    def _draw_image(self, pil_image, x_pos, y_pos, image_dimension):
        """
        Draw image onto page.

        :param Image pil_image: The image.
        :param int x_pos: The x position in inches.
        :param int y_pos: The y position in inches.
        :param list image_dimension: A 2-tuple containing the image width and
            height.
        """
        image = self._drawing.image(
            'data:{format};base64,{data}'.format(
                format=Image.MIME[pil_image.format],
                data=base64.b64encode(
                    open(pil_image.filename, 'rb').read()).decode('utf-8')),
            (x_pos * self.page_dpi, y_pos * self.page_dpi),
            (image_dimension[0] * self.page_dpi,
                image_dimension[1] * self.page_dpi))
        self._drawing.add(image)

    def _initialize_page(self):
        """
        Start a fresh page.
        """
        self._drawing = svgwrite.Drawing(
            '{}__page{:03d}.svg'.format(self.base_filename, self._page_number),
            size=(
                self.page_width * self.page_dpi,
                self.page_height * self.page_dpi),
            profile='full')
        self._page_number = self._page_number + 1

    def _render_page(self):
        """
        Render page.
        """
        self._drawing.save()

    def _draw_cutlines(self, cutline_config):
        """
        Draw cutlines.

        :param dict cutline_config: The cutline configuration.
        """
        self._drawing.defs.add(
            self._drawing.style(self.STYLESHEET.format(**cutline_config)))
        for line in self._cutline_set:
            self._drawing.add(self._drawing.line(
                (line.x0 * self.page_dpi, line.y0 * self.page_dpi),
                (line.x1 * self.page_dpi, line.y1 * self.page_dpi),
                class_='cutline'))
