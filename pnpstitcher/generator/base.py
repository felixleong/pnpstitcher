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
        pass

    def _draw_cutlines(self, cutline_set):
        """
        Draw cutlines.

        :param list cutline_set: The list of the cutlines.
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
        card_num_x, cut_margin_x = divmod(
            (self.page_width - self.page_margin_x * 2), image_dimension[0])
        card_num_y, cut_margin_y = divmod(
            (self.page_height - self.page_margin_y * 2), image_dimension[1])

        # Generate the vertical cutlines
        cutline_set = []
        prev_x = cut_margin_x / 2
        if not trim_offset:
            # If it's a clean cut, we need to draw the left-most cut line
            cutline_set.append(CutLine(prev_x, 0, prev_x, self.page_height))

        for cnt in range(card_num_x):
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
        prev_y = cut_margin_y / 2
        if not trim_offset:
            # If it's a clean cut, we need to draw the top-most cut line
            cutline_set.append(CutLine(0, prev_y, self.page_width, prev_y))

        for cnt in range(card_num_y):
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
