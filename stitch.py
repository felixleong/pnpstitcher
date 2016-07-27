"""PNP page stitcher.

Usage:
    pnp_stitch.py --output=FILENAME <files>...

Options:
    -o FILENAME, --output=FILENAME  The output PDF file.
"""
from docopt import docopt
from pint import UnitRegistry
from pnpstitcher.image import ImageSet
from pnpstitcher.generator import PdfGenerator


if __name__ == '__main__':
    arguments = docopt(__doc__, version='PNP Page Stitcher 0.1')
    output_fn = arguments['--output']
    filename_set = arguments['<files>']

    # NOTE TO SELF: Am going to make inches as the common unit, mainly on
    # the amount of the stuff that works w/ inches.
    ureg = UnitRegistry()
    Q_ = ureg.Quantity

    dpi = 300
    page_width = round(Q_('210mm').m_as('in') * dpi)
    page_height = round(Q_('297mm').m_as('in') * dpi)

    # Handle the files now
    image_set = ImageSet(filename_set)
    output_file = PdfGenerator(output_fn, page_width, page_height, dpi)
