"""Init file for the plugin."""

import logging

from qgis.PyQt.QtCore import QCoreApplication, QTranslator
from qgis.core import QgsApplication

from .processing_algorithms.provider import Provider
from .qgis_plugin_tools.tools.custom_logging import setup_logger, plugin_name
from .qgis_plugin_tools.tools.i18n import setup_translation

__copyright__ = 'Copyright 2019, 3Liz'
__license__ = 'GPL version 3'
__email__ = 'info@3liz.org'
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger(plugin_name())


class DrainSewerVisualInspection:
    def __init__(self, iface):
        _ = iface

        self.provider = None

        setup_logger(plugin_name())

        _, ts_file = setup_translation()
        if ts_file:
            self.translator = QTranslator()
            self.translator.load(ts_file)
            QCoreApplication.installTranslator(self.translator)

    def initProcessing(self):
        """Init Processing provider."""
        self.provider = Provider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        self.initProcessing()

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)
