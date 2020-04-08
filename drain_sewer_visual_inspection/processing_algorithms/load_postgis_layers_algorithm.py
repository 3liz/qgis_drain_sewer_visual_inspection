"""Load PostGIS layers algorithm."""

import logging

from collections import OrderedDict

from qgis.core import (
    QgsVectorLayer,
    Qgis,
    QgsWkbTypes,
    QgsDataSourceUri,
    QgsProcessingContext,
    QgsProcessingAlgorithm,
    QgsProcessingParameterString,
    QgsProcessingOutputMultipleLayers,
    QgsProcessingException,
)
from processing.tools import postgis

from ..qgis_plugin_tools.tools.custom_logging import plugin_name
from ..qgis_plugin_tools.tools.i18n import tr

__copyright__ = 'Copyright 2019, 3Liz'
__license__ = 'GPL version 3'
__email__ = 'info@3liz.org'
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger(plugin_name())

MAPPING = OrderedDict()  # Geometry name, Geometry type, primary key
MAPPING['file'] = [None, QgsWkbTypes.NullGeometry, 'id']
MAPPING['troncon'] = [None, QgsWkbTypes.NullGeometry, 'id']
MAPPING['obs'] = [None, QgsWkbTypes.NullGeometry, 'id']
MAPPING['regard'] = [None, QgsWkbTypes.NullGeometry, 'id']
MAPPING['geom_regard'] = ['Point', QgsWkbTypes.PointGeometry, 'id']
MAPPING['geom_troncon'] = ['LineString', QgsWkbTypes.LineGeometry, 'id']
MAPPING['geom_obs'] = ['Point', QgsWkbTypes.PointGeometry, 'id']
MAPPING['view_regard_geolocalized'] = ['Point', QgsWkbTypes.PointGeometry, 'id']


class LoadPostgisTables(QgsProcessingAlgorithm):

    DATABASE = 'DATABASE'
    SCHEMA = 'SCHEMA'
    OUTPUT_LAYERS = 'OUTPUT_LAYERS'

    LAYERS = (
        'file',
        'troncon',
        'obs',
        'regard',
        'geom_regard',
        'geom_troncon',
        'geom_obs',
        'view_regard_geolocalized',
    )

    def name(self):
        return 'load_postgis_layers'

    def displayName(self):
        return '{} {}'.format('01', tr('Load PostGIS layers'))

    def initAlgorithm(self, configuration):
        db_param = QgsProcessingParameterString(
            self.DATABASE,
            tr('Database (connection name)'),
        )
        db_param.setMetadata({
            'widget_wrapper': {
                'class': 'processing.gui.wrappers_postgis.ConnectionWidgetWrapper'}})
        self.addParameter(db_param)

        schema_param = QgsProcessingParameterString(
            self.SCHEMA,
            tr('Schema (schema name)'), 'public', False, True)
        schema_param.setMetadata({
            'widget_wrapper': {
                'class': 'processing.gui.wrappers_postgis.SchemaWidgetWrapper',
                'connection_param': self.DATABASE}})
        self.addParameter(schema_param)

        self.addOutput(
            QgsProcessingOutputMultipleLayers(
                self.OUTPUT_LAYERS,
                tr('Output layers')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        destination = self.parameterAsFile(parameters, self.DATABASE, context)

        try:
            db = postgis.GeoDB.from_name(destination)
            schema = self.parameterAsFile(parameters, self.SCHEMA, context)
        except QgsProcessingException:
            raise QgsProcessingException(
                tr('* ERROR while getting database "{}"').format(destination))

        database_uri = db.uri
        output_layers = []
        for table, geom in MAPPING.items():
            uri = QgsDataSourceUri(database_uri)
            if Qgis.QGIS_VERSION_INT >= 31000:
                uri.setTable(table)
                if geom[0]:
                    uri.setGeometryColumn('geom')
            else:
                uri_string = uri.uri(True)
                if geom[0]:
                    uri_string = uri_string.replace('table=""', 'table="{}" (geom)'.format(table))
                else:
                    uri_string = uri_string.replace('table=""', 'table="{}"'.format(table))
                uri = QgsDataSourceUri(uri_string)
            uri.setSchema(schema)  # Schema is updating the table name, so after search&replace
            uri.setKeyColumn(geom[2])

            dest_layer = QgsVectorLayer(uri.uri(False), table, 'postgres')

            if not dest_layer.isValid():
                raise QgsProcessingException(
                    tr('* ERROR: Can\'t load table "{}" in URI "{}"').format(table, uri.uri()))

            feedback.pushInfo('The layer {} has been loaded'.format(table))

            output_layers.append(dest_layer.id())

            # Add layer to project
            context.temporaryLayerStore().addMapLayer(dest_layer)
            context.addLayerToLoadOnCompletion(
                dest_layer.id(),
                QgsProcessingContext.LayerDetails(
                    table,
                    context.project(),
                    self.OUTPUT_LAYERS
                )
            )
        return {
            self.OUTPUT_LAYERS: output_layers
        }

    def group(self):
        return tr('Configuration')

    def groupId(self):
        return 'configuration'

    def createInstance(self):
        return self.__class__()
