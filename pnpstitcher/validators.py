import os.path
from pint import UnitRegistry
from tinycss2.color3 import parse_color
from voluptuous import Invalid


ureg = UnitRegistry()
Q_ = ureg.Quantity


def inches(value):
    """
    Validation and transform to inches.

    :param str value: The data value.
    :returns: The converted value in inches.
    :rtype: float
    """
    return Q_(value).m_as('in')


def csscolor(value):
    """
    Validation of CSS3 colours.

    :param str value: The data value.
    :returns: The original value.
    :rtype: str
    """
    parsed_color = parse_color(value)
    if parsed_color is None:
        raise Invalid('Invalid CSS color specified')

    return value


def file_exists(value):
    """
    Validate the file name one whether it exists or otherwise.

    :param str value: The data value as file name.
    :returns: The original value.
    :rtype: str
    """
    if os.path.exists(value) and os.path.isfile(value):
        return value
    else:
        raise Invalid('Invalid file')
