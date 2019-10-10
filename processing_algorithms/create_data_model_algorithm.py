"""Create data schema algorithm."""

import logging

from collections import OrderedDict

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsVectorLayer,
    QgsVectorLayerExporter,
)
from qgis.core import (
    QgsProcessingContext,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterCrs,
    QgsProcessingOutputMultipleLayers,
    QgsProcessingException,
)
from qgis.utils import spatialite_connect

from ..qgis_plugin_tools.custom_logging import plugin_name
from ..qgis_plugin_tools.resources import resources_path

__copyright__ = 'Copyright 2019, 3Liz'
__license__ = 'GPL version 3'
__email__ = 'info@3liz.org'
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger(plugin_name())

MAPPING = OrderedDict()
MAPPING['file'] = None
MAPPING['troncon'] = None
MAPPING['obs'] = None
MAPPING['regard'] = None
MAPPING['geom_regard'] = 'Point'
MAPPING['geom_troncon'] = 'LineString'
MAPPING['geom_obs'] = 'Point'


class CreateDataModelAlgorithm(QgsProcessingAlgorithm):

    DESTINATION = 'DESTINATION'
    CRS = 'CRS'
    OUTPUT_LAYERS = 'OUTPUT_LAYERS'

    def initAlgorithm(self, config):
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.DESTINATION,
                self.tr('Geopackage file'),
                fileFilter='gpkg'
            )
        )

        self.addParameter(
            QgsProcessingParameterCrs(
                self.CRS,
                self.tr('Coordinate Reference System'),
                defaultValue='EPSG:2154'
            )
        )

        self.addOutput(
            QgsProcessingOutputMultipleLayers(
                self.OUTPUT_LAYERS,
                self.tr('Output layers')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        base_name = self.parameterAsFile(parameters, self.DESTINATION, context)
        if not base_name.lower().endswith('.gpkg'):
            base_name += '.gpkg'
        uri = base_name

        crs = self.parameterAsCrs(parameters, self.CRS, context)

        options = dict()
        options['layerOptions'] = ['FID=id']
        options['fileEncoding'] = 'UTF-8'
        options['update'] = True

        for table, geom in MAPPING.items():
            # create virtual layer
            if geom:
                vl_path = '{}?crs={}&'.format(geom, crs.authid())
            else:
                vl_path = 'None?'

            csv_path = resources_path('data_models', '{}.csv'.format(table))
            csv = QgsVectorLayer(csv_path, table, 'ogr')
            if not csv.isValid():
                csv_path = resources_path('data_models', '{}.csv'.format(table))
                raise QgsProcessingException(
                    self.tr('* ERROR: Can\'t load CSV {}').format(csv_path))

            fields = []
            for c in csv.getFeatures():
                fields.append('field={}:{}'.format(c['name'], c['typeName']))
            del csv

            vl_path += '&'.join(fields)
            LOGGER.debug('Memory layer "{}" created with {}'.format(table, vl_path))
            vl = QgsVectorLayer(vl_path, table, 'memory')

            if vl.fields().count() != len(fields):
                raise QgsProcessingException(
                    self.tr('* ERROR while creating fields in layer "{}"'.format(table)))

            # export layer
            options['layerName'] = vl.name()
            exporter = QgsVectorLayerExporter(
                uri,
                'ogr',
                vl.fields(),
                vl.wkbType(),
                vl.sourceCrs(),
                True,
                options)

            # result
            if exporter.errorCode() != QgsVectorLayerExporter.NoError:
                raise QgsProcessingException(
                    self.tr('* ERROR while exporting the layer to {}:{}').format(uri, exporter.errorMessage()))

        output_layers = []
        for table in MAPPING.keys():
            # connection troncon_rereau_classif in geopackage
            dest_layer = QgsVectorLayer('{}|layername={}'.format(uri, table), table, 'ogr')
            if not dest_layer.isValid():
                raise QgsProcessingException(
                    self.tr('* ERROR: Can\'t load table "{}" in URI "{}"').format(table, uri))

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

        # Create a view
        view_name = 'view_regard_geolocalized'

        # Get connection
        conn = spatialite_connect(uri)

        # Do create view
        c = conn.cursor()
        sql = ("CREATE VIEW {} AS SELECT r.id, r.caa, r.id_geom_regard, r.id_file, g.geom "
               "FROM regard r, geom_regard g "
               "WHERE r.id_geom_regard = g.id;".format(view_name))
        feedback.pushInfo(sql)
        c.execute(sql)
        conn.commit()
        sql = ("INSERT INTO gpkg_contents (table_name, identifier, data_type, srs_id) "
               "VALUES ( '{0}', '{0}', 'features', {1});".format(view_name, crs.postgisSrid()))
        feedback.pushInfo(sql)
        c.execute(sql)
        conn.commit()
        sql = ("INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) "
               "VALUES ('{0}', 'geom', 'POINT', {1}, 0, 0);".format(view_name, crs.postgisSrid()))
        feedback.pushInfo(sql)
        c.execute(sql)
        conn.commit()

        conn.close()

        # Connexion à la couche view_regard_localized dans le Geopackage
        view_layer = QgsVectorLayer('{}|layername={}'.format(uri, view_name), view_name, 'ogr')
        if not view_layer.isValid():
            raise QgsProcessingException(
                self.tr('* ERROR: Can\'t load layer {} in {}').format(view_name, uri))

        output_layers.append(view_layer.id())

        # Add layer to project
        context.temporaryLayerStore().addMapLayer(view_layer)
        context.addLayerToLoadOnCompletion(
            view_layer.id(),
            QgsProcessingContext.LayerDetails(
                view_name,
                context.project(),
                self.OUTPUT_LAYERS
            )
        )

        feedback.pushInfo('The data model has been created in {}'.format(uri))

        return {
            self.DESTINATION: uri,
            self.OUTPUT_LAYERS: output_layers
        }

    def shortHelpString(self) -> str:
        return self.tr('Create the data model with all layers which are needed.')

    def name(self):
        return 'create_data_model'

    def displayName(self):
        return self.tr('00 Create data model')

    def group(self):
        return self.tr('Configuration')

    def groupId(self):
        return 'configuration'

    @staticmethod
    def tr(string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return self.__class__()
