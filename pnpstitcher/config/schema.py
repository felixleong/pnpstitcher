from voluptuous import (
    All,
    Any,
    Boolean,
    Coerce,
    Optional,
    Required,
    Schema,
    REMOVE_EXTRA)
from pnpstitcher.validators import inches, csscolor


_PAGE_SCHEMA = Schema({
    Required('dpi', default=300): Coerce(int),
    Required('width', default=inches('210mm')): All(str, inches),
    Required('height', default=inches('297mm')): All(str, inches),
    Required('margin_x', default=inches('3mm')): All(str, inches),
    Required('margin_y', default=inches('3mm')): All(str, inches),
}, extra=REMOVE_EXTRA)

_CUTLINE_SCHEMA = Schema({
    Required('color', default='#999999'): All(str, csscolor),
    Required('width', default=inches('1pp')): All(str, inches),
    Optional('dashed', default=True): Boolean(),
    Optional('trim_offset_x', default=0): All(str, inches),
    Optional('trim_offset_y', default=0): All(str, inches),
    Optional('round_corner', default=0): All(str, inches),
    Optional('layer', default='top'): All(str, Any('top', 'bottom')),
    Optional('style', default='cutthrough'): All(
        str, Any('cutthrough', 'inset'))
}, extra=REMOVE_EXTRA)

_SVG_SCHEMA = Schema({
    Required('page_dpi', default=96): Coerce(int),
}, extra=REMOVE_EXTRA)

CONFIG_SCHEMA = Schema({
    'page': _PAGE_SCHEMA,
    Optional('cutline', default=_CUTLINE_SCHEMA({})): _CUTLINE_SCHEMA,
    Optional('svg', default=_SVG_SCHEMA({})): _SVG_SCHEMA,
}, extra=REMOVE_EXTRA)