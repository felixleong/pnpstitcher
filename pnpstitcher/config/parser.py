from copy import deepcopy
from pint import UnitRegistry
from pnpstitcher.config.default import DEFAULT_CONFIG
from tinycss2.color3 import parse_color
import configparser


def load_config(config_filename=None):
    """
    Load the configuration file.

    :param str config_filename: The configuration filename.
    :returns: The parsed and validated configuration.
    :rtype: dict
    """
    config = deepcopy(DEFAULT_CONFIG)

    if config_filename:
        parser = configparser.ConfigParser()
        parser.read(config_filename)

        for key in config.keys():
            if key in parser:
                config[key].update(parser[key])

    __normalize(config)

    return config


def __normalize(config):
    """
    Normalize the config parameters.

    :param dict config: The configuration dictionary.
    """
    ureg = UnitRegistry()
    Q_ = ureg.Quantity

    # Convert all the page related parameter to pixels
    dpi = int(config['page']['dpi'])
    config['page']['dpi'] = dpi
    config['page']['width'] = Q_(config['page']['width']).m_as('in')
    config['page']['height'] = Q_(config['page']['height']).m_as('in')
    config['page']['margin_x'] = Q_(config['page']['margin_x']).m_as('in')
    config['page']['margin_y'] = Q_(config['page']['margin_y']).m_as('in')

    # Convert the cutline configuration
    config['cutline']['color'] = parse_color(config['cutline']['color'])
    config['cutline']['width'] = float(config['cutline']['width'])
    config['cutline']['dashed'] = config['cutline']['dashed'] == 'true'
    config['cutline']['trim_offset'] = (
        Q_(config['cutline']['trim_offset']).m_as('in'))
    if config['cutline']['layer'] not in ('top', 'bottom'):
        raise ValueError(
            'Cutline layer config takes either "top" or "bottom".')
