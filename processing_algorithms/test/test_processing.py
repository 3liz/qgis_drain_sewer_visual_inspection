import tempfile
import os

from qgis.PyQt.QtCore import QCoreApplication, QSettings
from qgis.testing import unittest, start_app
from qgis.core import QgsApplication, QgsCoordinateReferenceSystem, QgsVectorLayer

import sys
if not hasattr(sys, 'argv'):
    sys.argv = ['']

start_app()

try:
    import processing
except ImportError:
    from qgis import processing

from ..provider import Provider
from ...qgis_plugin_tools.resources import plugin_test_data_path


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

    def test_layer(self):
        """Quick test for the layer."""
        layer_path = plugin_test_data_path('manholes_to_import.geojson')
        layer = QgsVectorLayer(layer_path, 'test', 'ogr')
        self.assertTrue(layer.isValid(), '{} is not valid'.format(layer_path))

    def test_create_geopackage(self):
        """Test the workflow about DSVI."""
        # Geopackage for testing
        geopackage_path = os.path.join(tempfile.mkdtemp(), 'test.gpkg')

        # Create geopackage
        params = {
            'FILE_GPKG': geopackage_path,
            'CRS': QgsCoordinateReferenceSystem('EPSG:2154')}
        result = processing.run(
            'drain_sewer_visual_inspection:create_geopackage', params)

        self.assertTrue(os.path.exists(result['FILE_GPKG']))
        for layer in result['OUTPUT_LAYERS']:
            self.assertTrue(layer.isValid())

        # Setting up the project
        params = {
            'TABLE_FICHIER': '{}|layername=file'.format(geopackage_path),
            'TABLE_TRONCON': '{}|layername=troncon'.format(geopackage_path),
            'TABLE_OBSERVATIONS': '{}|layername=obs'.format(geopackage_path),
            'TABLE_REGARD': '{}|layername=regard'.format(geopackage_path),
            'COUCHE_GEOM_REGARD': '{}|layername=geom_regard'.format(geopackage_path),
            'COUCHE_GEOM_TRONCON': '{}|layername=geom_troncon'.format(geopackage_path),
            'COUCHE_GEOM_OBSERVATION': '{}|layername=geom_obs'.format(geopackage_path),
            'VIEW_REGARD_GEOLOCALIZED': '{}|layername=view_regard_geolocalized'.format(geopackage_path),
        }
        result = processing.run('drain_sewer_visual_inspection:config_dsvi_project', params)

        # Import regard into geopackage
        layer_path = plugin_test_data_path('manholes_to_import.geojson')
        layer = QgsVectorLayer(layer_path, 'test', 'ogr')
        self.assertTrue(layer.isValid())
        params = {
            'COUCHE_A_IMPORTER': layer,
            'CHAMP_NOM_REGARD': 'name',
            'COUCHE_GEOM_REGARD': '{}|layername=geom_regard'.format(geopackage_path)
        }
        result = processing.run("drain_sewer_visual_inspection:import_geom_regard", params)
