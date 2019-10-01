from PyQt5.QtCore import QCoreApplication, QSettings
from qgis.testing import unittest, start_app
from qgis.core import QgsApplication, QgsCoordinateReferenceSystem

import sys
if not hasattr(sys, 'argv'):
    sys.argv = ['']

start_app()

try:
    import processing
except ImportError:
    from qgis import processing

from ..provider import Provider


class ProcessingTest(unittest.TestCase):

    def __init__(self, methodName):
        """Run before all tests and set up environment"""
        super().__init__(methodName)

        # Don't mess with actual user settings
        QCoreApplication.setOrganizationName("Trying")
        QCoreApplication.setOrganizationDomain("qgis.org")
        QCoreApplication.setApplicationName("QGIS-DSVI")
        QSettings().clear()

        # make Provider settings available
        self.provider = Provider()
        self.provider.load()

    def setUp(self) -> None:
        QgsApplication.processingRegistry().addProvider(self.provider)
        processing.Processing.initialize()

    def test_processing(self):
        for alg in QgsApplication.processingRegistry().algorithms():
            print(alg.id(), "->", alg.displayName())

    def test_create_geopackage(self):
        params = {
            'FILE_GPKG': '/tmp/processing_605a277cecad4784a82aca33d9c21c03/c06e4a949d014c95a76bcd38a93e7e3d/FILE_GPKG.file',
            'CRS': QgsCoordinateReferenceSystem('EPSG:2154')}
        result = processing.run(
            'drain_sewer_visual_inspection:create_geopackage', params)
