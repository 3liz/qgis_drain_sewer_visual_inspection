"""Init file for the plugin."""

__copyright__ = "Copyright 2019, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = '$Format:%H$'

from .plugin import DrainSewerVisualInspection


def classFactory(iface):
    return DrainSewerVisualInspection(iface)
