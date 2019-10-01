import tempfile
import os

from qgis.PyQt.QtCore import QCoreApplication, QSettings
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
        QCoreApplication.setOrganizationName('MyOrganization')
        QCoreApplication.setOrganizationDomain('qgis.org')
        QCoreApplication.setApplicationName('QGIS-DSVI')
        QSettings().clear()

        self.provider = Provider()

    def setUp(self) -> None:
        QgsApplication.processingRegistry().addProvider(self.provider)
        processing.Processing.initialize()

    def test_create_geopackage(self):
        """Test the workflow about DSVI."""
        path = os.path.join(tempfile.mkdtemp(), 'test.gpkg')
        params = {
            'FILE_GPKG': path,
            'CRS': QgsCoordinateReferenceSystem('EPSG:2154')}
        result = processing.run(
            'drain_sewer_visual_inspection:create_geopackage', params)

        self.assertTrue(os.path.exists(result['FILE_GPKG']))
        for layer in result['OUTPUT_LAYERS']:
            self.assertTrue(layer.isValid())

        params = {
            'TABLE_FICHIER': '{}|layername=file'.format(path),
            'TABLE_TRONCON': '{}|layername=troncon'.format(path),
            'TABLE_OBSERVATIONS': '{}|layername=obs'.format(path),
            'TABLE_REGARD': '{}|layername=regard'.format(path),
            'COUCHE_GEOM_REGARD': '{}|layername=geom_regard'.format(path),
            'COUCHE_GEOM_TRONCON': '{}|layername=geom_troncon'.format(path),
            'COUCHE_GEOM_OBSERVATION': '{}|layername=geom_obs'.format(path),
            'VIEW_REGARD_GEOLOCALIZED': '{}|layername=view_regard_geolocalized'.format(path),
        }
        processing.run('drain_sewer_visual_inspection:config_dsvi_project', params)
