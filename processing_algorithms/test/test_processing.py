from qgis.testing import unittest, start_app
from qgis.core import QgsApplication, QgsCoordinateReferenceSystem

start_app()

try:
    import processing
except ImportError:
    from qgis import processing

from ..provider import Provider


class ProcessingTest(unittest.TestCase):

    def setUpClass(cls) -> None:
        QgsApplication.processingRegistry().addProvider(Provider())
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
