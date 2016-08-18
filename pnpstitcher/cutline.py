from collections import namedtuple


CutLine = namedtuple('CutLine', ['x0', 'y0', 'x1', 'y1'])


class CutlineGenerator(object):
    def __init__(self, page_config, cutline_config):
        """
        Constructor.

        :param dict page_config: The page configuration.
        :param dict cutline_config: The cutline configuration.
        """
        self._page_config = page_config
        self._cutline_config = cutline_config

        self.card_num_x = 0
        self.card_num_y = 0
        self.cut_margin_x = 0
        self.cut_margin_y = 0
        self.cutline_set = None

    def generate(self, image_catalog):
        """
        Generate the cutline based on the images fed.

        :param ImageCatalog image_catalog: The image catalog.
        """
        # Get the image dimensions
        image_dimension = image_catalog.image_size
        self._image_width = image_dimension[0] / self._page_config['dpi']
        self._image_height = image_dimension[1] / self._page_config['dpi']

        # Get the page meta
        card_num_x, cut_margin_x = divmod(
            round(
                self._page_config['width'] -
                self._page_config['margin_x'] * 2),
            self._image_width)
        card_num_y, cut_margin_y = divmod(
            round(
                self._page_config['height'] -
                self._page_config['margin_y'] * 2),
            self._image_height)

        self.card_num_x = int(card_num_x)
        self.card_num_y = int(card_num_y)
        self.cut_margin_x = cut_margin_x / 2 + self._page_config['margin_x']
        self.cut_margin_y = cut_margin_y / 2 + self._page_config['margin_y']

        # Validation
        if self.card_num_x == 0 or self.card_num_y == 0:
            raise RuntimeError('Image too large for the page')

        # Generate the cutline
        method = getattr(
            self, '_generate_{}'.format(self._cutline_config['style']))
        self.cutline_set = method()
        return self.cutline_set

    def _generate_inset(self):
        """
        Generate the inset style of cutlines.

        This style would draw the cutline around the card that we want to cut,
        which would be useful for a cutting machine.
        """
        cutline_set = []

        # Generate the vertical cutlines
        trim_x = self._cutline_config['trim_offset_x']
        trim_y = self._cutline_config['trim_offset_y']

        prev_y = self.cut_margin_y
        for cnt_y in range(self.card_num_y):
            prev_x = self.cut_margin_x

            for cnt_x in range(self.card_num_x):
                cutline_set.append(CutLine(
                    # Top-left corner
                    prev_x + trim_x,
                    prev_y + trim_y,

                    # Bottom-right corner
                    prev_x + self._image_width - trim_x,
                    prev_y + self._image_height - trim_y))

                prev_x = prev_x + self._image_width

            prev_y = prev_y + self._image_height

        return cutline_set

    def _generate_cutthrough(self):
        """
        Generate the cut-through style of cutlines.

        This style would draw lines across the whole page so that the person
        can easily cut through the whole sheet of paper using a guillotine or
        rotary cutter.
        """
        cutline_set = []
        page_width = self._page_config['width']
        page_height = self._page_config['height']

        # Generate the vertical cutlines
        trim_x = self._cutline_config['trim_offset_x']
        trim_y = self._cutline_config['trim_offset_y']
        prev_x = self.cut_margin_x
        if not trim_x:
            # If it's a clean cut, we need to draw the left-most cut line
            cutline_set.append(CutLine(prev_x, 0, prev_x, page_height))

        for cnt in range(self.card_num_x):
            next_x = prev_x + self._image_width
            if trim_x:
                left_cut = prev_x + trim_x
                right_cut = next_x - trim_x
                cutline_set.append(CutLine(left_cut, 0, left_cut, page_height))
                cutline_set.append(CutLine(
                    right_cut, 0, right_cut, page_height))
            else:
                cutline_set.append(CutLine(
                    next_x, 0, next_x, page_height))

            prev_x = next_x

        # Generate the horizontal cutlines
        prev_y = self.cut_margin_y
        if not trim_y:
            # If it's a clean cut, we need to draw the top-most cut line
            cutline_set.append(CutLine(0, prev_y, page_width, prev_y))

        for cnt in range(self.card_num_y):
            next_y = prev_y + self._image_height
            if trim_y:
                top_cut = prev_y + trim_y
                bottom_cut = next_y - trim_y
                cutline_set.append(CutLine(0, top_cut, page_width, top_cut))
                cutline_set.append(CutLine(
                    0, bottom_cut, page_width, bottom_cut))
            else:
                cutline_set.append(CutLine(0, next_y, page_width, next_y))

            prev_y = next_y

        return cutline_set
