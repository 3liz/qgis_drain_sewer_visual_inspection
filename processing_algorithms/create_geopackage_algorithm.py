"""Create geopackage algorithm."""

import logging
import os

from collections import OrderedDict

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsVectorLayer,
    QgsVectorFileWriter,
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


class CreateGeopackageAlgorithm(QgsProcessingAlgorithm):
    FILE_GPKG = 'FILE_GPKG'
    CRS = 'CRS'
    OUTPUT_LAYERS = 'OUTPUT_LAYERS'

    def initAlgorithm(self, config):
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.FILE_GPKG,
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
        base_name = self.parameterAsFile(parameters, self.FILE_GPKG, context)
        if not base_name.lower().endswith('.gpkg'):
            base_name += '.gpkg'

        crs = self.parameterAsCrs(parameters, self.CRS, context)

        encoding = 'UTF-8'
        driver_name = QgsVectorFileWriter.driverForExtension('gpkg')

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

            # set create file layer options
            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = driver_name
            options.fileEncoding = encoding

            options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile
            if os.path.exists(base_name):
                options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer

            options.layerName = vl.name()
            options.layerOptions = ['FID=id']

            # write file
            write_result, error_message = QgsVectorFileWriter.writeAsVectorFormat(
                vl,
                base_name,
                options)

            # result
            if write_result != QgsVectorFileWriter.NoError:
                raise QgsProcessingException(
                    self.tr('* ERROR: {}').format(error_message))

        output_layers = []
        for table in MAPPING.keys():
            # connection troncon_rereau_classif in geopackage
            dest_layer = QgsVectorLayer('{}|layername={}'.format(base_name, table), table, 'ogr')
            if not dest_layer.isValid():
                raise QgsProcessingException(
                    self.tr('* ERROR: Can\'t load layer {} in {}').format(table, base_name))

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
        conn = spatialite_connect(base_name)

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
        view_layer = QgsVectorLayer('{}|layername={}'.format(base_name, view_name), view_name, 'ogr')
        if not view_layer.isValid():
            raise QgsProcessingException(
                self.tr('* ERROR: Can\'t load layer {} in {}').format(view_name, base_name))

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

        feedback.pushInfo('The geopackage {} has been created'.format(base_name))

        return {
            self.FILE_GPKG: base_name,
            self.OUTPUT_LAYERS: output_layers
        }

    def shortHelpString(self) -> str:
        return self.tr('Create the geopackage with all layers which are needed.')

    def name(self):
        return 'create_geopackage'

    def displayName(self):
        return self.tr('00 Create geopackage')

    def group(self):
        return self.tr('Configuration')

    def groupId(self):
        return 'configuration'

    @staticmethod
    def tr(string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return self.__class__()
