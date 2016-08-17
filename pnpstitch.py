"""PNP page stitcher.

Usage:
    pnpstitch.py --output=FILENAME --format=FORMAT [--config=FILENAME --rtl] <files>...

Options:
    -o FILENAME --output=FILENAME       Name of the output file.
    -f FORMAT --format=FORMAT           The file format, supports either "pdf"
                                        or "svg".
    -c FILENAME --config=FILENAME       Name of the config file.
    -r --rtl                            Layout the cards from right-to-left for
                                        duplex printing.
    <files>                             The PNG files to be stitched together.
"""
from docopt import docopt
from pnpstitcher.config import (
    ConfigParser,
    CONFIG_SCHEMA,
    DEFAULT_CONFIG)
from pnpstitcher.image import ImageCatalog
from pnpstitcher.generator import PdfGenerator, SvgGenerator
from pnpstitcher.validators import file_exists
from voluptuous import (
    All,
    Any,
    Optional,
    Schema)


__OPT_SCHEMA = Schema({
    '--output': str,
    '--format': Any('pdf', 'svg'),
    Optional('--config'): Any(None, file_exists),
    Optional('--rtl', default=False): bool,
    '<files>': [file_exists],
})


if __name__ == '__main__':
    arguments = __OPT_SCHEMA(
        docopt(__doc__, version='PNP Page Stitcher 0.1'))

    output_fn = arguments['--output']
    config_fn = arguments['--config']
    file_format = arguments['--format']
    rtl = arguments['--rtl']
    filename_set = arguments['<files>']

    # Load the configuration file
    parser = ConfigParser()
    if config_fn:
        parser.read(config_fn)
        config = CONFIG_SCHEMA(parser.as_dict())
    else:
        config = CONFIG_SCHEMA(DEFAULT_CONFIG)

    # Handle the files now
    image_catalog = ImageCatalog(filename_set)
    if file_format == 'pdf':
        output_generator = PdfGenerator(
            output_fn, config['page']['width'], config['page']['height'],
            config['page']['margin_x'], config['page']['margin_y'],
            config['page']['dpi'], 72)
    elif file_format == 'svg':
        output_generator = SvgGenerator(
            output_fn, config['page']['width'], config['page']['height'],
            config['page']['margin_x'], config['page']['margin_y'],
            config['page']['dpi'], 96)
    else:
        raise RuntimeError('Unsupported output file format')

    output_generator.generate(image_catalog, config['cutline'], rtl)
