"""PNP page duplexer.

Usage:
    pnpduplex.py --output=FILENAME <front_pdf> <back_pdf>

Options:
    -o FILENAME --output=FILENAME   Name of the duplexed PDF output.
    <front_pdf>                     The PDF file containing the front pages.
    <back_pdf>                      The PDF file containing the back pages.
"""
from docopt import docopt
from pdfrw import PdfReader, PdfWriter


if __name__ == '__main__':
    arguments = docopt(__doc__, version='PNP Page Duplexer 0.1')
    output_fn = arguments['--output']
    front_fn = arguments['<front_pdf>']
    back_fn = arguments['<back_pdf>']

    front_pdf = PdfReader(front_fn).pages
    back_pdf = PdfReader(back_fn).pages

    # Validation
    if len(front_pdf) - len(back_pdf) != 0:
        raise RuntimeError('The number of pages are not equal')

    # Then we would start to duplex the pages and write the file
    output_pdf = PdfWriter()
    for x in range(len(front_pdf)):
        output_pdf.addpage(front_pdf[x])
        output_pdf.addpage(back_pdf[x])

    output_pdf.write(output_fn)
