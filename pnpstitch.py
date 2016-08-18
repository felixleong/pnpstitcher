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
from pnpstitcher.cutline import CutlineGenerator
from pnpstitcher.output import PdfGenerator, SvgGenerator
from pnpstitcher.validators import file_exists
from voluptuous import (
    Any,
    Optional,
    Schema)
import os.path


__OPT_SCHEMA = Schema({
    '--output': str,
    '--format': Any('pdf', 'svg'),
    Optional('--config'): Any(None, file_exists),
    Optional('--rtl', default=False): bool,
    '<files>': [file_exists],
})
__DEFAULT_CONFIG_PATH = [
    '$HOME/.config/pnpstitch.ini',
    './pnpstitch.ini',
]


def __load_default_config():
    for fn in __DEFAULT_CONFIG_PATH:
        full_fn = os.path.expandvars(fn)
        if os.path.isfile(full_fn):
            parser = ConfigParser()
            parser.read(full_fn)
            return CONFIG_SCHEMA(parser.as_dict())

    # If none of the config works out, we would just load our in app default
    # config
    parser = ConfigParser()
    config = CONFIG_SCHEMA(DEFAULT_CONFIG)
    return config


if __name__ == '__main__':
    arguments = __OPT_SCHEMA(
        docopt(__doc__, version='PNP Page Stitcher 0.1'))

    output_fn = arguments['--output']
    config_fn = arguments['--config']
    file_format = arguments['--format']
    rtl = arguments['--rtl']
    filename_set = arguments['<files>']

    # Load the configuration file
    if config_fn:
        parser = ConfigParser()
        parser.read(config_fn)
        config = CONFIG_SCHEMA(parser.as_dict())
    else:
        config = __load_default_config()

    # Setup the generators
    if file_format == 'pdf':
        OutputGenerator = PdfGenerator
        page_dpi = 72
    elif file_format == 'svg':
        OutputGenerator = SvgGenerator
        page_dpi = config['svg']['page_dpi']
    else:
        raise RuntimeError('Unsupported output file format')

    # Output the file
    image_catalog = ImageCatalog(filename_set)
    cutline_generator = CutlineGenerator(config['page'], config['cutline'])
    cutline_generator.generate(image_catalog)
    output_generator = OutputGenerator(
        output_fn, cutline_generator, config['page'], page_dpi)

    output_generator.generate(image_catalog, config['cutline'], rtl)
