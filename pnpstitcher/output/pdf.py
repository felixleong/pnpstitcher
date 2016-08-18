from pnpstitcher.output.base import BaseGenerator
from tinycss2.color3 import parse_color
import cairocffi as cairo
import math


class PdfGenerator(BaseGenerator):
    def __init__(self, filename, cutline_generator, page_config, page_dpi):
        """
        Constructor.

        :param str filename: The filename of the output PDF file.
        :param CutlineGenerator cutline_generator: The cutline generator.
        :param dict page_config: The page configuration.
        :param int page_dpi: The page dpi.
        """
        super(PdfGenerator, self).__init__(
            filename, cutline_generator, page_config, page_dpi)

        # Set the page and drawing context
        self._pdf = cairo.PDFSurface(
            self.filename,
            page_config['width'] * page_dpi,
            page_config['height'] * page_dpi)
        self._context = cairo.Context(self._pdf)

    def _draw_image(self, pil_image, x_pos, y_pos, image_dimension):
        """
        Draw image onto page.

        :param Image pil_image: The image.
        :param int x_pos: The x position in inches.
        :param int y_pos: The y position in inches.
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
        # DOES NOTHING, a new page would have been created during render page.
        return

    def _render_page(self):
        """
        Render page.
        """
        self._pdf.show_page()

    def _draw_cutlines(self, cutline_set, cutline_config):
        """
        Draw cutlines.

        :param list cutline_set: The list of cutlines.
        :param dict cutline_config: The cutline configuration.
        """
        self._set_cutline_style(cutline_config)
        super(PdfGenerator, self)._draw_cutlines(cutline_set, cutline_config)
        self._context.stroke()

    def _draw_cutlines_cutthrough(self, cutline_set, cutline_config):
        """
        Draw cut-through cutlines.

        :param list cutline_set: The list of cutlines.
        :param dict cutline_config: The cutline configuration.
        """
        # Draw lines
        for line in cutline_set:
            self._context.move_to(
                line.x0 * self.page_dpi, line.y0 * self.page_dpi)
            self._context.line_to(
                line.x1 * self.page_dpi, line.y1 * self.page_dpi)

    def _draw_cutlines_inset(self, cutline_set, cutline_config):
        """
        Draw inset cutlines.

        :param list cutline_set: The list of cutlines.
        :param dict cutline_config: The cutline configuration.
        """
        # Draw all the inset rectangles
        for line in cutline_set:
            if cutline_config['round_corner']:
                self._draw_rounded_rectangle(
                    line, cutline_config['round_corner'])
            else:
                self._context.rectangle(
                    line.x0 * self.page_dpi, line.y0 * self.page_dpi,
                    (line.x1 - line.x0) * self.page_dpi,
                    (line.y1 - line.y0) * self.page_dpi)

    def _set_cutline_style(self, cutline_config):
        """
        Set the cutline style.

        :param dict cutline_config: The cutline configuration.
        """
        # Set the style
        self._context.set_source_rgba(*parse_color(cutline_config['color']))
        self._context.set_line_width(cutline_config['width'] * self.page_dpi)
        if cutline_config['dashed']:
            self._context.set_dash((4, 4), 0)

    def _draw_rounded_rectangle(self, line, round_corner):
        """
        Draw rounded rectangle.

        :param Cutline line: The cutline definition.
        :param float round_corner: The radius length of the round corner.
        """
        self._context.new_sub_path()
        self._context.arc(
            (line.x0 + round_corner) * self.page_dpi,
            (line.y0 + round_corner) * self.page_dpi,
            round_corner * self.page_dpi,
            math.radians(180), math.radians(270))
        self._context.arc(
            (line.x1 - round_corner) * self.page_dpi,
            (line.y0 + round_corner) * self.page_dpi,
            round_corner * self.page_dpi,
            math.radians(-90), math.radians(0))
        self._context.arc(
            (line.x1 - round_corner) * self.page_dpi,
            (line.y1 - round_corner) * self.page_dpi,
            round_corner * self.page_dpi,
            math.radians(0), math.radians(90))
        self._context.arc(
            (line.x0 + round_corner) * self.page_dpi,
            (line.y1 - round_corner) * self.page_dpi,
            round_corner * self.page_dpi,
            math.radians(90), math.radians(180))
        self._context.close_path()

    def _draw_registration_crosshair(self, registration_config):
        """
        Draw a crosshair registration mark.

        :param dict registration_config: The registration mark configuration.
        """
        size = registration_config['size']
        half_size = registration_config['size'] / 2
        circle_size = registration_config['size'] * 0.35

        self._context.save()
        self._context.set_source_rgba(0, 0, 0, 1)
        self._context.set_line_width(1)
        self._context.move_to(
            (registration_config['x_pos'] + half_size) * self.page_dpi,
            registration_config['y_pos'] * self.page_dpi)
        self._context.line_to(
            (registration_config['x_pos'] + half_size) * self.page_dpi,
            (registration_config['y_pos'] + size) * self.page_dpi)

        self._context.move_to(
            registration_config['x_pos'] * self.page_dpi,
            (registration_config['y_pos'] + half_size) * self.page_dpi)
        self._context.line_to(
            (registration_config['x_pos'] + size) * self.page_dpi,
            (registration_config['y_pos'] + half_size) * self.page_dpi)

        self._context.arc(
            (registration_config['x_pos'] + half_size) * self.page_dpi,
            (registration_config['y_pos'] + (size * 0.5)) * self.page_dpi,
            circle_size * self.page_dpi,
            math.radians(0), math.radians(360))
        self._context.stroke()
        self._context.restore()

    def _draw_registration_square(self, registration_config):
        """
        Draw a square registration mark.

        :param dict registration_config: The registration mark configuration.
        """
        self._context.save()
        self._context.set_source_rgba(0, 0, 0, 1)
        self._context.rectangle(
            registration_config['x_pos'] * self.page_dpi,
            registration_config['y_pos'] * self.page_dpi,
            registration_config['size'] * self.page_dpi,
            registration_config['size'] * self.page_dpi)
        self._context.fill()
        self._context.restore()
