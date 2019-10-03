from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingParameterVectorLayer,
    QgsProcessingOutputNumber,
    QgsProcessingException,
)
from qgis.core import (
    QgsFeature,
    QgsCoordinateTransform,
)

from ..qgis_plugin_tools.tools.fields import provider_fields

__copyright__ = "Copyright 2019, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = '$Format:%H$'


class ImportGeomRegardAlgorithm(QgsProcessingAlgorithm):


    COUCHE_A_IMPORTER = 'COUCHE_A_IMPORTER'
    CHAMP_NOM_REGARD = 'CHAMP_NOM_REGARD'
    COUCHE_GEOM_REGARD = 'COUCHE_GEOM_REGARD'

    SUCCESS = 'SUCCESS'

    def initAlgorithm(self, config):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.COUCHE_A_IMPORTER,
                self.tr('Couche des regards à importer'),
                [QgsProcessing.TypeVectorPoint]
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.CHAMP_NOM_REGARD,
                self.tr('Champs du nom des regards à conserver'),
                None,
                self.COUCHE_A_IMPORTER,
                QgsProcessingParameterField.Any
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.COUCHE_GEOM_REGARD,
                self.tr('Couche des géométries de regards'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        self.addOutput(QgsProcessingOutputNumber(self.SUCCESS, self.tr('Succès')))

    def processAlgorithm(self, parameters, context, feedback):
        g_import = self.parameterAsSource(parameters, self.COUCHE_A_IMPORTER, context)
        g_label = self.parameterAsString(parameters, self.CHAMP_NOM_REGARD, context)
        g_regard = self.parameterAsVectorLayer(parameters, self.COUCHE_GEOM_REGARD, context)

        # Construction des objets regards
        xform = QgsCoordinateTransform(g_import.sourceCrs(), g_regard.crs(), context.project())
        features = []
        fields = provider_fields(g_regard.fields())
        for feat in g_import.getFeatures():
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                return {self.SUCCESS: 0}

            geometry = feat.geometry()
            if geometry is None:
                # TODO check utility?
                continue

            feat_i = QgsFeature(fields)
            feat_i.setAttribute('label', feat[g_label])

            geometry.transform(xform)
            feat_i.setGeometry(geometry)
            features.append(feat_i)

        # Stop the algorithm if cancel button has been clicked
        if feedback.isCanceled():
            return {self.SUCCESS: 0}

        # Ajout des objets regards
        if features:
            g_regard.startEditing()
            (res, outFeats) = g_regard.dataProvider().addFeatures(features)
            if not res or not outFeats:
                raise QgsProcessingException(
                    self.tr('* ERREUR: lors de l\'enregistrement des regards %s') % ', '.join(g_regard.dataProvider().errors()))
            if not g_regard.commitChanges():
                raise QgsProcessingException(
                    self.tr('* ERROR: Commit %s.') % g_regard.commitErrors())

        feedback.pushInfo('Manholes have been imported')
        return {self.SUCCESS: 1}

    def shortHelpString(self) -> str:
        return self.tr('It will import the geometry and the specified field into the layer "geom_regard".')

    def name(self):
        return 'import_geom_regard'

    def displayName(self):
        return self.tr('10 Import des géométries de regards')

    def group(self):
        return self.tr('Configuration')

    def groupId(self):
        return 'configuration'

    @staticmethod
    def tr(string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return self.__class__()
