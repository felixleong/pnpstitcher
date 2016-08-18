from PIL import Image
import base64
from pnpstitcher.output.base import BaseGenerator
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
        }}
        .dashed {{
            fill: none;
            stroke: {color};
            stroke-width: {width};
            stroke-linecap: butt;
            stroke-linejoin: miter;
            stroke-opacity: 1;
            stroke-dasharray: 6, 6;
        }}
    """

    def __init__(self, filename, cutline_generator, page_config, page_dpi):
        """
        Constructor.

        :param str filename: The filename of the output PDF file.
        :param CutlineGenerator cutline_generator: The cutline generator.
        :param dict page_config: The page configuration.
        :param int page_dpi: The page dpi.
        """
        super(SvgGenerator, self).__init__(
            filename, cutline_generator, page_config, page_dpi)
        self.base_filename, self.ext = os.path.splitext(filename)
        self._page_number = 1
        self._drawing = None
        self._border_width = None

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
                self.page_config['width'] * self.page_dpi,
                self.page_config['height'] * self.page_dpi),
            profile='full')
        self._page_number = self._page_number + 1

    def _render_page(self):
        """
        Render page.
        """
        self._drawing.save()

    def _draw_cutlines(self, cutline_set, cutline_config):
        """
        Draw cutlines.

        :param list cutline_set: The list of cutlines.
        :param dict cutline_config: The cutline configuration.
        """
        if self._border_width is None:
            self._border_width = cutline_config['width'] * self.page_dpi
        cutline_config['width'] = self._border_width

        self._drawing.defs.add(
            self._drawing.style(self.STYLESHEET.format(**cutline_config)))
        super(SvgGenerator, self)._draw_cutlines(cutline_set, cutline_config)

    def _draw_cutlines_cutthrough(self, cutline_set, cutline_config):
        """
        Draw cut-through cutlines.

        :param list cutline_set: The list of cutlines.
        :param dict cutline_config: The cutline configuration.
        """
        if cutline_config['dashed']:
            class_name = 'dashed'
        else:
            class_name = 'cutline'

        for line in cutline_set:
            self._drawing.add(self._drawing.line(
                (line.x0 * self.page_dpi, line.y0 * self.page_dpi),
                (line.x1 * self.page_dpi, line.y1 * self.page_dpi),
                class_=class_name))

    def _draw_cutlines_inset(self, cutline_set, cutline_config):
        """
        Draw inset cutlines.

        :param list cutline_set: The list of cutlines.
        :param dict cutline_config: The cutline configuration.
        """
        if cutline_config['dashed']:
            class_name = 'dashed'
        else:
            class_name = 'cutline'

        self._drawing.defs.add(
            self._drawing.style(self.STYLESHEET.format(**cutline_config)))
        for line in cutline_set:
            self._drawing.add(self._drawing.rect(
                (line.x0 * self.page_dpi, line.y0 * self.page_dpi),
                ((line.x1 - line.x0) * self.page_dpi,
                    (line.y1 - line.y0) * self.page_dpi),
                ry=(cutline_config['round_corner'] * self.page_dpi),
                class_=class_name))
