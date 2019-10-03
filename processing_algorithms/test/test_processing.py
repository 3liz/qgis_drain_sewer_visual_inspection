import tempfile
import os

from shutil import copyfile

from qgis.PyQt.QtCore import QCoreApplication, QSettings
from qgis.testing import unittest, start_app
from qgis.core import QgsApplication, QgsCoordinateReferenceSystem, QgsVectorLayer

import sys
if not hasattr(sys, 'argv'):
    sys.argv = ['']

start_app()

try:
    from qgis import processing
except ImportError:
    import processing

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
        QgsApplication.processingRegistry().addProvider(self.provider)

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
            'FILE_TABLE': '{}|layername=file'.format(geopackage_path),
            'SEGMENTS_TABLE': '{}|layername=troncon'.format(geopackage_path),
            'OBSERVATIONS_TABLE': '{}|layername=obs'.format(geopackage_path),
            'MANHOLES_TABLE': '{}|layername=regard'.format(geopackage_path),
            'GEOM_MANHOLES': '{}|layername=geom_regard'.format(geopackage_path),
            'GEOM_SEGMENT': '{}|layername=geom_troncon'.format(geopackage_path),
            'GEOM_OBSERVATION': '{}|layername=geom_obs'.format(geopackage_path),
            'VIEW_MANHOLES_GEOLOCALIZED': '{}|layername=view_regard_geolocalized'.format(geopackage_path),
        }
        result = processing.run('drain_sewer_visual_inspection:config_dsvi_project', params)
        self.assertEqual(len(result), 0)
        print('First algo done')

        # Import regard into geopackage
        layer_path = plugin_test_data_path('manholes_to_import.geojson')
        layer = QgsVectorLayer(layer_path, 'test', 'ogr')
        self.assertTrue(layer.isValid())
        params = {
            'INPUT': layer,
            'MANHOLE_NAME_FIELD': 'name',
            'GEOM_MANHOLES': '{}|layername=geom_regard'.format(geopackage_path)
        }
        result = processing.run('drain_sewer_visual_inspection:import_geom_regard', params)
        self.assertEqual(result['MAN_HOLES'], layer.featureCount())

        # The next part is using some confidential private data
        list_files = []
        path = plugin_test_data_path('confidential')
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith('.txt'):
                    list_files.append(os.path.join(root, file))
                if file.endswith('.TXT'):
                    list_files.append(os.path.join(root, file))

        print('Going to import {} files:'.format(len(list_files)))
        for itv_file in list_files:
            print('Importing {}'.format(itv_file))
            params = {
                'INPUT': itv_file,
                'FILE_TABLE': '{}|layername=file'.format(geopackage_path),
                'SEGMENT_TABLE': '{}|layername=troncon'.format(geopackage_path),
                'OBSERVATIONS_TABLE': '{}|layername=obs'.format(geopackage_path),
                'MANHOLES_TABLE': '{}|layername=regard'.format(geopackage_path),
            }
            result = processing.run('drain_sewer_visual_inspection:import_dsvi_data', params)
            self.assertEqual(result['SUCCESS'], 1)

        print(geopackage_path)

        copyfile(geopackage_path, plugin_test_data_path('confidential', 'test.gpkg'))
