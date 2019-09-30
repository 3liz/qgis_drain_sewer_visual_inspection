"""Create geopackage algorithm."""

import os.path

from pathlib import Path
from shutil import copyfile

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessingContext,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFileDestination,
    QgsProcessingOutputMultipleLayers,
    QgsProcessingException,
)
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsFields,
    QgsField,
    QgsVectorLayer,
    QgsVectorFileWriter,
)
from qgis.utils import spatialite_connect


from ..qgis_plugin_tools.resources import resources_path

__copyright__ = "Copyright 2019, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = '$Format:%H$'


class CreateGeopackageAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    processing_algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing processing_algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    # OUTPUT = 'OUTPUT'
    # INPUT = 'INPUT'

    FILE_GPKG = 'FILE_GPKG'
    OUTPUT_LAYERS = 'OUTPUT_LAYERS'


    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.FILE_GPKG,
                self.tr('Geopackage file'),
                fileFilter='gpkg'
            )
        )

        self.addOutput(
            QgsProcessingOutputMultipleLayers(
                self.OUTPUT_LAYERS,
                self.tr('Output layers')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        base_name = self.parameterAsFile(parameters, self.FILE_GPKG, context)
        parent_base_name = str(Path(base_name).parent)
        if not base_name.endswith('.gpkg'):
            base_name = os.path.join(parent_base_name, Path(base_name).stem+'.gpkg')

        tables = [
            'file',
            'troncon',
            'obs',
            'regard',
            'geom_regard',
            'geom_troncon',
            'geom_obs',
            'calc_obs',
            'calc_geom_troncon',
        ]

        geometries = {
            'file': 'None',
            'troncon': 'None',
            'obs': 'None',
            'regard': 'None',
            'geom_regard': 'Point',
            'geom_troncon': 'LineString',
            'geom_obs': 'Point',
            'calc_obs': 'None',
            'calc_geom_troncon': 'None',
        }

        encoding = 'UTF-8'
        driverName = QgsVectorFileWriter.driverForExtension('gpkg')
        crs = QgsCoordinateReferenceSystem('EPSG:2154')

        for table in tables:
            # create virtual layer
            vl_path = geometries[table]
            if vl_path != 'None':
                vl_path = "{}?crs={}".format(geometries[table], crs.authid())
            vl = QgsVectorLayer(vl_path, table, 'memory')
            pr = vl.dataProvider()

            # define fields
            fields = QgsFields()

            csv_path = resources_path('data_models', '{}.csv'.format(table))
            csv = QgsVectorLayer(csv_path, table, 'ogr')
            if not csv.isValid():
                csv_path = resources_path('data_models', '{}.csv'.format(table))
                raise QgsProcessingException(
                    self.tr('* ERROR: Can\'t load CSV {}').format(csv_path))

            for c in csv.getFeatures():
                fields.append(QgsField(name=c['name'], type=c['type']))

            del csv

            # add fields
            pr.addAttributes(fields)
            vl.updateFields()  # tell the vector layer to fetch changes from the provider

            # set create file layer options
            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = driverName
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

            del fields
            del pr
            del vl

        # copie du ficher xls
        copyfile(
            resources_path('data_models', 'norme13508_2_simplified_with_rule.xls'),
            os.path.join(parent_base_name, 'regles_norme13508_2.xls'))

        output_layers = []
        for table in tables:
            # Connexion à la couche troncon_rerau_classif dans le Geopackage
            dest_layer = QgsVectorLayer('{}|layername={}'.format(base_name, table), table, 'ogr')
            if not dest_layer.isValid():
                raise QgsProcessingException(
                    self.tr('* ERROR: Can\'t load layer {} in {}').format(table, base_name))

            feedback.pushInfo('The layer {} has been created'.format(table))

            output_layers.append(dest_layer)
            # Ajout de la couche au projet
            context.temporaryLayerStore().addMapLayer(dest_layer)
            context.addLayerToLoadOnCompletion(
                dest_layer.id(),
                QgsProcessingContext.LayerDetails(
                    table,
                    context.project(),
                    self.OUTPUT_LAYERS
                )
            )

        # lecture du fichier xls pour la norme
        dest_layer = QgsVectorLayer(os.path.join(parent_base_name, 'regles_norme13508_2.xls'), 'regles_norme13508_2', 'ogr')
        if not dest_layer.isValid():
            raise QgsProcessingException(
                self.tr('* ERROR: Can\'t load XLS layer in {}').format(parent_base_name))

        output_layers.append(dest_layer)

        # Ajout de la couche troncon_rerau_classif au projet
        context.temporaryLayerStore().addMapLayer(dest_layer)
        context.addLayerToLoadOnCompletion(
            dest_layer.id(),
            QgsProcessingContext.LayerDetails(
                'regles_norme13508_2',
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
                self.tr('* ERROR: Can\'t load layer {} in {}').format(view_name , base_name))

        output_layers.append(view_layer)
        # Ajout de la couche au projet
        context.temporaryLayerStore().addMapLayer(view_layer)
        context.addLayerToLoadOnCompletion(
            view_layer.id(),
            QgsProcessingContext.LayerDetails(
                view_name,
                context.project(),
                self.OUTPUT_LAYERS
            )
        )

        return {self.FILE_GPKG: base_name, self.OUTPUT_LAYERS: output_layers}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'create_geopackage'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('00 Create geopackage')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('Configuration')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'configuration'

    @staticmethod
    def tr(string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return self.__class__()
