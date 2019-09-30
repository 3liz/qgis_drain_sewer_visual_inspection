"""Init file for the plugin."""

import logging

from qgis.core import QgsApplication
from qgis.PyQt.QtCore import QCoreApplication, QTranslator
from qgis.PyQt.QtWidgets import QAction, QMessageBox

from .processing_algorithms.provider import Provider
from .qgis_plugin_tools.custom_logging import setup_logger, plugin_name
from .qgis_plugin_tools.i18n import setup_translation, tr

__copyright__ = "Copyright 2019, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger(plugin_name())


class DrainSewerVisualInspection:
    def __init__(self, iface):

        self.iface = iface
        self.action = None
        self.provider = None

        setup_logger(plugin_name())

        ts_file = setup_translation()
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
        self.action = QAction(tr('Go!'), self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action
        QgsApplication.processingRegistry().removeProvider(self.provider)

    def run(self):
        QMessageBox.information(None, tr('Minimal plugin'), tr('Do something useful here'))
