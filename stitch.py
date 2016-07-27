"""PNP page stitcher.

Usage:
    pnp_stitch.py <files>...
"""
from PIL import Image
from pint import UnitRegistry
from docopt import docopt
from collections import namedtuple
import cairocffi as cairo


CutLine = namedtuple('CutLine', ['x0', 'y0', 'x1', 'y1', 'length'])


def get_common_dimension(file_set):
    """
    Get the common dimension.

    :param list file_set: The list of files.
    :returns: A 2-tuple containing width and height.
    :type: tuple.
    """
    base_size = Image.open(file_set[0]).size
    for fn in file_set:
        image = Image.open(fn)
        if base_size != image.size:
            raise RuntimeError(
                'Unmatched dimension. File: {}, expected dimension: {}'.format(
                    fn, base_size))

    return base_size


def generate_cut_line(
        paper_dimension, image_dimension, page_margin_x=0, page_margin_y=0,
        trim_offset=0):
    """
    Generate the page frame meta.

    :param tuple paper_dimension: A 2-tuple containing the width and height of
        the page in pixels.
    :param tuple image_dimension: A 2-tuple containing the width and height of
        the card images in pixels.
    :param int page_margin_x: The paper margin on the x-axis in pixels (both
        sides).
    :param int page_margin_y: The paper margin on the y-axis in pixels (both
        sides).
    :param int trim_offset: The trim offset in pixels.
    :returns: The metadata of the page.
    """
    page_width = paper_dimension[0]
    page_height = paper_dimension[1]
    card_num_x, cut_margin_x = divmod(
        (paper_dimension[0] - page_margin_x * 2), image_dimension[0])
    card_num_y, cut_margin_y = divmod(
        (paper_dimension[1] - page_margin_y * 2),
        image_dimension[1])

    # Generate the vertical cutlines
    cutline_set = []
    prev_x = cut_margin_x / 2
    if not trim_offset:
        # If it's a clean cut, we need to draw the left-most cut line
        cutline_set.append(CutLine(
            prev_x, 0, prev_x, page_height, page_height))

    for cnt in range(card_num_x):
        next_x = prev_x + image_dimension[0]
        if trim_offset:
            left_cut = prev_x + trim_offset
            right_cut = next_x - trim_offset
            cutline_set.append(CutLine(
                left_cut, 0, left_cut, page_height, page_height))
            cutline_set.append(CutLine(
                right_cut, 0, right_cut, page_height, page_height))
        else:
            cutline_set.append(CutLine(
                next_x, 0, next_x, page_height, page_height))

        prev_x = next_x

    # Generate the horizontal cutlines
    prev_y = cut_margin_y / 2
    if not trim_offset:
        # If it's a clean cut, we need to draw the top-most cut line
        cutline_set.append(CutLine(
            0, prev_y, page_width, prev_y, page_width))

    for cnt in range(card_num_y):
        next_y = prev_y + image_dimension[1]
        if trim_offset:
            top_cut = prev_y + trim_offset
            bottom_cut = next_y - trim_offset
            cutline_set.append(CutLine(
                0, top_cut, page_width, top_cut, page_width))
            cutline_set.append(CutLine(
                0, bottom_cut, page_width, bottom_cut, page_width))
        else:
            cutline_set.append(CutLine(
                0, next_y, page_width, next_y, page_width))

        prev_y = next_y

    return cutline_set


def get_pdf_context(
        filename, page_width, page_height, dpi):
    """
    :param str filename: The filename of the output PDF file.
    :param int page_width: Page width in pixel.
    :param int page_height: Page height in pixel.
    :param int dpi: The dpi.
    """
    dpi_to_pp = 72 / dpi

    # Set the page and drawing context
    pdf = cairo.PDFSurface(
        filename, page_width * dpi_to_pp, page_height * dpi_to_pp)
    context = cairo.Context(pdf)
    context.scale(dpi_to_pp, dpi_to_pp)

    return pdf, context


def draw_cutlines(context, cutline_set):
    """
    Draw cutlines.

    :param cairo.Context context: The context of drawing surface.
    :param list cutline_set: The list of the cutlines.
    """
    # Set the style
    context.set_source_rgba(0.6, 0.6, 0.6, 1)
    context.set_line_width(1)
    context.set_dash((30, 15), 0)

    # Draw lines
    for line in cutline_set:
        context.move_to(line.x0, line.y0)
        context.line_to(line.x1, line.y1)

    # Paint the lines
    context.stroke()


if __name__ == '__main__':
    arguments = docopt(__doc__, version='PNP Page Stitcher 0.1')
    file_set = arguments['<files>']

    # NOTE TO SELF: Am going to make inches as the common unit, mainly on
    # the amount of the stuff that works w/ inches.
    ureg = UnitRegistry()
    Q_ = ureg.Quantity

    dpi = 300
    paper_width = round(Q_('210mm').m_as('in') * dpi)
    paper_height = round(Q_('297mm').m_as('in') * dpi)

    # Handle the files now
    dimension = get_common_dimension(file_set)
    cutline_set = generate_cut_line((paper_width, paper_height), dimension)

    # Generate the PDF
    pdf, context = get_pdf_context(
        'output.pdf', paper_width, paper_height, dpi)
    draw_cutlines(context, cutline_set)
    pdf.show_page()
    draw_cutlines(context, cutline_set)
    pdf.show_page()
    draw_cutlines(context, cutline_set)
    pdf.show_page()
