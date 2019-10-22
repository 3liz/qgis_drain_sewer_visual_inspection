"""Create data schema algorithm."""

import logging
import psycopg2

from collections import OrderedDict

from qgis.core import (
    QgsVectorLayer,
    QgsVectorLayerExporter,
    Qgis,
    QgsWkbTypes,
    QgsDataSourceUri,
    QgsProcessingContext,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterCrs,
    QgsProcessingParameterString,
    QgsProcessingOutputMultipleLayers,
    QgsProcessingException,
)
from qgis.utils import spatialite_connect
from processing.tools import postgis


from ..qgis_plugin_tools.tools.custom_logging import plugin_name
from ..qgis_plugin_tools.tools.i18n import tr
from ..qgis_plugin_tools.tools.resources import resources_path

__copyright__ = 'Copyright 2019, 3Liz'
__license__ = 'GPL version 3'
__email__ = 'info@3liz.org'
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger(plugin_name())

MAPPING = OrderedDict()  # Geometry name, Geometry type, sequence
MAPPING['file'] = [None, QgsWkbTypes.NullGeometry, 'id']
MAPPING['troncon'] = [None, QgsWkbTypes.NullGeometry, None]
MAPPING['obs'] = [None, QgsWkbTypes.NullGeometry, 'id']
MAPPING['regard'] = [None, QgsWkbTypes.NullGeometry, None]
MAPPING['geom_regard'] = ['Point', QgsWkbTypes.PointGeometry, 'id']
MAPPING['geom_troncon'] = ['LineString', QgsWkbTypes.LineGeometry, 'id']
MAPPING['geom_obs'] = ['Point', QgsWkbTypes.PointGeometry, None]


class CreateDataModelAlgorithm(QgsProcessingAlgorithm):

    DESTINATION = 'DESTINATION'
    SCHEMA = 'SCHEMA'
    CRS = 'CRS'
    OUTPUT_LAYERS = 'OUTPUT_LAYERS'
    VIEW_NAME = 'view_regard_geolocalized'

    def initAlgorithm(self, config):

        self.addParameter(
            QgsProcessingParameterCrs(
                self.CRS,
                tr('Coordinate Reference System'),
                defaultValue='EPSG:2154'
            )
        )

        self.addOutput(
            QgsProcessingOutputMultipleLayers(
                self.OUTPUT_LAYERS,
                tr('Output layers')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        destination = self.parameterAsFile(parameters, self.DESTINATION, context)

        try:
            db = postgis.GeoDB.from_name(destination)
            is_geopackage = False
            schema = self.parameterAsFile(parameters, self.SCHEMA, context)
        except QgsProcessingException:
            is_geopackage = True
            schema = None

        if is_geopackage:
            if not destination.lower().endswith('.gpkg'):
                destination += '.gpkg'
            uri = destination
        else:
            database_uri = db.uri
            info = database_uri.connectionInfo(True)
            conn = psycopg2.connect(info)
            c = conn.cursor()
            sql = "DROP VIEW IF EXISTS {}.{};".format(schema, self.VIEW_NAME)
            feedback.pushInfo(sql)
            c.execute(sql)
            conn.commit()

        crs = self.parameterAsCrs(parameters, self.CRS, context)

        options = dict()
        options['update'] = True

        if is_geopackage:
            options['layerOptions'] = ['FID=id']
            options['fileEncoding'] = 'UTF-8'

        output_layers = []
        for table, geom in MAPPING.items():
            # create virtual layer
            if geom[0]:
                vl_path = '{}?crs={}&'.format(geom[0], crs.authid())
            else:
                vl_path = 'None?'

            csv_path = resources_path('data_models', '{}.csv'.format(table))
            csv = QgsVectorLayer(csv_path, table, 'ogr')
            if not csv.isValid():
                csv_path = resources_path('data_models', '{}.csv'.format(table))
                raise QgsProcessingException(
                    tr('* ERROR: Can\'t load CSV {}').format(csv_path))

            fields = []
            for c in csv.getFeatures():
                fields.append('field={}:{}'.format(c['name'], c['typeName']))
            del csv

            vl_path += '&'.join(fields)
            LOGGER.debug('Memory layer "{}" created with {}'.format(table, vl_path))
            vl = QgsVectorLayer(vl_path, table, 'memory')

            if vl.fields().count() != len(fields):
                raise QgsProcessingException(
                    tr('* ERROR while creating fields in layer "{}"'.format(table)))

            # export layer
            options['layerName'] = vl.name()
            if not is_geopackage:
                uri = QgsDataSourceUri(database_uri)
                if Qgis.QGIS_VERSION_INT >= 31000:
                    uri.setTable(vl.name())
                    if vl.isSpatial():
                        uri.setGeometryColumn('geom')
                else:
                    uri_string = uri.uri(True)
                    if vl.isSpatial():
                        uri_string = uri_string.replace('table=""', 'table="{}" (geom)'.format(vl.name()))
                    else:
                        uri_string = uri_string.replace('table=""', 'table="{}"'.format(vl.name()))
                    uri = QgsDataSourceUri(uri_string)
                uri.setSchema(schema)  # Schema is updating the table name, so after search&replace
                uri.setKeyColumn(vl.fields().at(0).name())

            exporter = QgsVectorLayerExporter(
                uri if is_geopackage else uri.uri(),
                'ogr' if is_geopackage else 'postgres',
                vl.fields(),
                vl.wkbType(),
                vl.crs(),
                True,
                options)

            # result
            if exporter.errorCode() != QgsVectorLayerExporter.NoError:
                source = uri if is_geopackage else uri.uri()
                raise QgsProcessingException(
                    tr('* ERROR while exporting the layer to "{}":"{}"').format(source, exporter.errorMessage()))

            # Do create sequence
            if geom[2] and not is_geopackage:
                c = conn.cursor()
                sql = "CREATE SEQUENCE {}.{}_{}_seq;".format(schema, table, geom[2])
                c.execute(sql)
                conn.commit()
                sql = "ALTER TABLE {0}.{1} ALTER COLUMN {2} SET DEFAULT nextval('{0}.{1}_{2}_seq'::regclass);".format(schema, table, geom[2])
                c.execute(sql)
                conn.commit()

            # connection troncon_rereau_classif in geopackage
            if is_geopackage:
                dest_layer = QgsVectorLayer('{}|layername={}'.format(uri, table), table, 'ogr')
            else:
                uri = QgsDataSourceUri(database_uri)
                if Qgis.QGIS_VERSION_INT >= 31000:
                    uri.setTable(vl.name())
                    if vl.isSpatial():
                        uri.setGeometryColumn('geom')
                else:
                    uri_string = uri.uri(True)
                    if vl.isSpatial():
                        uri_string = uri_string.replace('table=""', 'table="{}" (geom)'.format(vl.name()))
                    else:
                        uri_string = uri_string.replace('table=""', 'table="{}"'.format(vl.name()))
                    uri = QgsDataSourceUri(uri_string)
                uri.setSchema(schema)  # Schema is updating the table name, so after search&replace
                uri.setKeyColumn(vl.fields().at(0).name())
                dest_layer = QgsVectorLayer(uri.uri(False), table, 'postgres')
            if not dest_layer.isValid():
                source = uri if is_geopackage else uri.uri()
                raise QgsProcessingException(
                    tr('* ERROR: Can\'t load table "{}" in URI "{}"').format(table, source))

            feedback.pushInfo('The layer {} has been created'.format(table))

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

        # Get connection
        if is_geopackage:
            conn = spatialite_connect(uri)

        # Do create view
        c = conn.cursor()
        prefix = ''
        view_destination = self.VIEW_NAME
        if not is_geopackage:
            prefix = '{}.'.format(schema)
            view_destination = '{}{}'.format(prefix, view_destination)
        sql = ("CREATE VIEW {0} AS SELECT r.id, r.caa, r.id_geom_regard, r.id_file, g.geom "
               "FROM {1}regard r, {1}geom_regard g "
               "WHERE r.id_geom_regard = g.id;".format(view_destination, prefix))
        feedback.pushInfo(sql)
        c.execute(sql)
        conn.commit()

        if is_geopackage:
            sql = ("INSERT INTO gpkg_contents (table_name, identifier, data_type, srs_id) "
                   "VALUES ( '{0}', '{0}', 'features', {1});".format(self.VIEW_NAME, crs.postgisSrid()))
            feedback.pushInfo(sql)
            c.execute(sql)
            conn.commit()
            sql = ("INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) "
                   "VALUES ('{0}', 'geom', 'POINT', {1}, 0, 0);".format(self.VIEW_NAME, crs.postgisSrid()))
            feedback.pushInfo(sql)
            c.execute(sql)
            conn.commit()

        conn.close()

        # Connexion à la couche view_regard_localized dans le Geopackage
        if is_geopackage:
            view_layer = QgsVectorLayer('{}|layername={}'.format(uri, self.VIEW_NAME), self.VIEW_NAME, 'ogr')
        else:
            uri = QgsDataSourceUri(database_uri)
            if Qgis.QGIS_VERSION_INT >= 31000:
                uri.setTable(self.VIEW_NAME)
                uri.setGeometryColumn('geom')
            else:
                uri_string = uri.uri(True)
                uri_string = uri_string.replace('table=""', 'table="{}" (geom)'.format(self.VIEW_NAME))
                uri = QgsDataSourceUri(uri_string)
            uri.setSchema(schema)  # Schema is updating the table name, so after search&replace
            uri.setKeyColumn('id')
            view_layer = QgsVectorLayer(uri.uri(False), self.VIEW_NAME, 'postgres')
        if not view_layer.isValid():
            source = uri if is_geopackage else uri.uri()
            raise QgsProcessingException(
                tr('* ERROR: Can\'t load layer {} in {}').format(self.VIEW_NAME, source))

        output_layers.append(view_layer.id())

        # Add layer to project
        context.temporaryLayerStore().addMapLayer(view_layer)
        context.addLayerToLoadOnCompletion(
            view_layer.id(),
            QgsProcessingContext.LayerDetails(
                self.VIEW_NAME,
                context.project(),
                self.OUTPUT_LAYERS
            )
        )

        feedback.pushInfo('The data model has been created in {}'.format(uri))

        return {
            self.DESTINATION: uri,
            self.OUTPUT_LAYERS: output_layers
        }

    def group(self):
        return tr('Configuration')

    def groupId(self):
        return 'configuration'

    def createInstance(self):
        return self.__class__()


class CreateGeopackage(CreateDataModelAlgorithm):

    def name(self):
        return 'create_geopackage_data_model'

    def displayName(self):
        return '{} {}'.format('02', tr('Create geopackage data model'))

    def initAlgorithm(self, configuration):
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.DESTINATION,
                tr('Geopackage file'),
                fileFilter='gpkg'
            )
        )
        super().initAlgorithm(configuration)

    def shortHelpString(self) -> str:
        return tr('Create the data model with a new geopackage.')


class CreatePostgisTables(CreateDataModelAlgorithm):

    def name(self):
        return 'create_postgis_data_model'

    def displayName(self):
        return '{} {}'.format('00', tr('Create PostGIS data model'))

    def initAlgorithm(self, configuration):
        db_param = QgsProcessingParameterString(
            self.DESTINATION,
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
                'connection_param': self.DESTINATION}})
        self.addParameter(schema_param)

        super().initAlgorithm(configuration)

    def shortHelpString(self) -> str:
        tables = ', '.join(MAPPING.keys())
        return tr(
            'Create the data model in a PostGIS schema.\n'
            'Be careful, all these tables are going to be replaced: {} '
            'and the view "{}" in the given schema.\n'
            'The given schema must exist before.'
        ).format(tables, self.VIEW_NAME)
