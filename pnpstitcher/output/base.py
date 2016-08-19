from abc import ABCMeta


class BaseGenerator(object):
    __metaclass__ = ABCMeta

    def __init__(self, filename, cutline_generator, page_config, page_dpi):
        """
        Constructor.

        :param str filename: The filename of the output PDF file.
        :param CutlineGenerator cutline_generator: The cutline generator.
        :param dict page_config: The page configuration.
        :param int page_dpi: The page dpi.
        """
        self.filename = filename
        self.cutline_generator = cutline_generator
        self.page_config = page_config
        self.image_dpi = page_config['dpi']
        self.page_dpi = page_dpi
        self.image_scale = self.page_dpi / self.image_dpi

    def generate(
            self, image_catalog, cutline_config, registration_config,
            rtl=False):
        """
        Generate the output file.

        :param ImageCatalog image_catalog: The loaded image database.
        :param dict cutline_config: The cutline configuration.
        :param dict registration_config: The registration mark configuration.
        :param bool rtl: Layout the images from right-to-left.
        """
        # Initialize all the page detail
        image_width = image_catalog.image_size[0] / self.image_dpi
        image_height = image_catalog.image_size[1] / self.image_dpi
        origin_x = self.cutline_generator.cut_margin_x
        x_inc = image_width
        if rtl:
            origin_x = (
                origin_x +
                (image_width * (self.cutline_generator.card_num_x - 1)))
            x_inc = -image_width

        # Generate the images
        x_cnt = 0
        y_cnt = 0
        x_pos = origin_x
        y_pos = self.cutline_generator.cut_margin_y
        for pil_image in image_catalog.image_set:
            # Draw cut lines if it's a fresh page
            if x_cnt == 0 and y_cnt == 0:
                self._initialize_page()
                if cutline_config['layer'] == 'bottom':
                    self._draw_cutlines(
                        self.cutline_generator.cutline_set, cutline_config)

            # Draw the image
            if self.page_config['mode'] in ('full', 'image'):
                self._draw_image(
                    pil_image, x_pos, y_pos, (image_width, image_height))

            # Switch to next row when it is happening
            x_cnt = x_cnt + 1
            x_pos = x_pos + x_inc
            if x_cnt >= self.cutline_generator.card_num_x:
                x_cnt = 0
                y_cnt = y_cnt + 1

                x_pos = origin_x
                y_pos = y_pos + image_height

            # If we got past the page threshold, we would need to cease it
            if y_cnt >= self.cutline_generator.card_num_y:
                y_cnt = 0
                y_pos = self.cutline_generator.cut_margin_y
                self._finalize_page(cutline_config, registration_config)

        # After we hit the last page and if there's some left-over that is not
        # rendered, we should do it now.
        if x_cnt != 0 or y_cnt != 0:
            self._finalize_page(cutline_config, registration_config)

    def _initialize_page(self):
        """
        Start a fresh page.
        """
        raise NotImplemented()

    def _render_page(self):
        """
        Render page.
        """
        raise NotImplemented()

    def _draw_image(self, image, x_pos, y_pos, image_dimension):
        """
        Draw image onto page.

        :param Image image: The image.
        :param int x_pos: The x position in inches.
        :param int y_pos: The y position in inches.
        :param list image_dimension: A 2-tuple containing the image width and
            height.
        """
        raise NotImplemented()

    def _draw_cutlines_cutthrough(self, cutline_set, cutline_config):
        """
        Draw cut-through cutlines.

        :param list cutline_set: The list of cutlines.
        :param dict cutline_config: The cutline configuration.
        """
        raise NotImplemented()

    def _draw_cutlines_inset(self, cutline_set, cutline_config):
        """
        Draw inset cutlines.

        :param list cutline_set: The list of cutlines.
        :param dict cutline_config: The cutline configuration.
        """
        raise NotImplemented()

    def _draw_registration_crosshair(self, registration_config):
        """
        Draw a crosshair registration mark.

        :param dict registration_config: The registration mark configuration.
        """
        raise NotImplemented()

    def _draw_registration_square(self, registration_config):
        """
        Draw a square registration mark.

        :param dict registration_config: The registration mark configuration.
        """
        raise NotImplemented()

    def _draw_cutlines(self, cutline_set, cutline_config):
        """
        Draw cutlines.

        :param list cutline_set: The list of cutlines.
        :param dict cutline_config: The cutline configuration.
        """
        # If it's image mode, we would skip this
        if not self.page_config['mode'] in ('full', 'cutline'):
            return

        # Decide which style of cutline to draw
        if cutline_config['style'] == 'cutthrough':
            self._draw_cutlines_cutthrough(cutline_set, cutline_config)
        elif cutline_config['style'] == 'inset':
            self._draw_cutlines_inset(cutline_set, cutline_config)
        else:
            raise RuntimeError('Unexpected cut line style')

    def _draw_registration(self, registration_config):
        """
        Draw a registration mark.

        :param dict registration_config: The registration mark configuration.
        """
        if registration_config['type'] == 'crosshair':
            self._draw_registration_crosshair(registration_config)
        elif registration_config['type'] == 'square':
            self._draw_registration_square(registration_config)
        else:
            raise RuntimeError('Unexpected registration mark type')

    def _finalize_page(self, cutline_config, registration_config):
        """
        Finalize the drawing in the page.

        :param dict cutline_config: The cutline configuration.
        :param dict registration_config: The registration mark configuration.
        """
        if cutline_config['layer'] == 'top':
            self._draw_cutlines(
                self.cutline_generator.cutline_set, cutline_config)

        if self.page_config['registration']:
            self._draw_registration(registration_config)

        self._render_page()
