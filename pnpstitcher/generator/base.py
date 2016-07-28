from collections import namedtuple


CutLine = namedtuple('CutLine', ['x0', 'y0', 'x1', 'y1'])


class BaseGenerator(object):
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
        self.page_width = page_width
        self.page_height = page_height
        self.page_margin_x = page_margin_x
        self.page_margin_y = page_margin_y
        self.dpi = dpi

    def generate(self, image_catalog, cutline_config):
        """
        Generate the output file.

        :param ImageCatalog image_catalog: The loaded image database.
        :param dict cutline_config: The cutline configuration.
        """
        self._generate_cut_line(
            image_catalog.image_size, cutline_config['trim_offset'])
        self._render(image_catalog, cutline_config)

    def _render(self, image_set, cutline_config):
        """
        Render the images on pages.

        :param ImageSet image_set: The loaded image database.
        :param dict cutline_config: The cutline configuration.
        """
        raise NotImplemented()

    def _draw_cutlines(self, cutline_config):
        """
        Draw cutlines.

        :param dict cutline_config: The cutline configuration.
        """
        raise NotImplemented()

    def _generate_cut_line(self, image_dimension, trim_offset=0):
        """
        Generate the page frame meta.

        :param tuple image_dimension: A 2-tuple containing the width and height
            of the card images in pixels.
        :param int trim_offset: The trim offset in pixels.
        :returns: The metadata of the page.
        """
        self._card_num_x, self._cut_margin_x = divmod(
            (self.page_width - self.page_margin_x * 2), image_dimension[0])
        self._card_num_y, self._cut_margin_y = divmod(
            (self.page_height - self.page_margin_y * 2), image_dimension[1])
        self._cut_margin_x = self._cut_margin_x / 2 + self.page_margin_x
        self._cut_margin_y = self._cut_margin_y / 2 + self.page_margin_y

        # Generate the vertical cutlines
        cutline_set = []
        prev_x = self._cut_margin_x
        if not trim_offset:
            # If it's a clean cut, we need to draw the left-most cut line
            cutline_set.append(CutLine(prev_x, 0, prev_x, self.page_height))

        for cnt in range(self._card_num_x):
            next_x = prev_x + image_dimension[0]
            if trim_offset:
                left_cut = prev_x + trim_offset
                right_cut = next_x - trim_offset
                cutline_set.append(CutLine(
                    left_cut, 0, left_cut, self.page_height))
                cutline_set.append(CutLine(
                    right_cut, 0, right_cut, self.page_height))
            else:
                cutline_set.append(CutLine(
                    next_x, 0, next_x, self.page_height))

            prev_x = next_x

        # Generate the horizontal cutlines
        prev_y = self._cut_margin_y
        if not trim_offset:
            # If it's a clean cut, we need to draw the top-most cut line
            cutline_set.append(CutLine(0, prev_y, self.page_width, prev_y))

        for cnt in range(self._card_num_y):
            next_y = prev_y + image_dimension[1]
            if trim_offset:
                top_cut = prev_y + trim_offset
                bottom_cut = next_y - trim_offset
                cutline_set.append(CutLine(
                    0, top_cut, self.page_width, top_cut))
                cutline_set.append(CutLine(
                    0, bottom_cut, self.page_width, bottom_cut))
            else:
                cutline_set.append(CutLine(0, next_y, self.page_width, next_y))

            prev_y = next_y

        self._cutline_set = cutline_set
