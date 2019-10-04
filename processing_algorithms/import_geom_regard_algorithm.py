from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsFeature,
    QgsCoordinateTransform,
)
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingParameterVectorLayer,
    QgsProcessingOutputNumber,
    QgsProcessingException,
)

from ..qgis_plugin_tools.tools.fields import provider_fields

__copyright__ = 'Copyright 2019, 3Liz'
__license__ = 'GPL version 3'
__email__ = 'info@3liz.org'
__revision__ = '$Format:%H$'


class ImportGeomRegardAlgorithm(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    MANHOLE_NAME_FIELD = 'MANHOLE_NAME_FIELD'
    GEOM_MANHOLES = 'GEOM_MANHOLES'

    MAN_HOLES = 'MAN_HOLES'

    def initAlgorithm(self, config):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Couche des regards à importer'),
                [QgsProcessing.TypeVectorPoint]
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.MANHOLE_NAME_FIELD,
                self.tr('Champs du nom des regards à conserver'),
                None,
                self.INPUT,
                QgsProcessingParameterField.Any
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.GEOM_MANHOLES,
                self.tr('Couche des géométries de regards'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        self.addOutput(QgsProcessingOutputNumber(self.MAN_HOLES, self.tr('Number of imported man holes')))

    def processAlgorithm(self, parameters, context, feedback):
        g_import = self.parameterAsSource(parameters, self.INPUT, context)
        g_label = self.parameterAsString(parameters, self.MANHOLE_NAME_FIELD, context)
        g_regard = self.parameterAsVectorLayer(parameters, self.GEOM_MANHOLES, context)

        # Construction des objets regards
        xform = QgsCoordinateTransform(g_import.sourceCrs(), g_regard.crs(), context.project())
        features = []
        fields = provider_fields(g_regard.fields())
        i = 0
        for feat in g_import.getFeatures():
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                return {self.MAN_HOLES: 0}

            geometry = feat.geometry()
            if geometry is None:
                # TODO check utility?
                continue

            feat_i = QgsFeature(fields)
            feat_i.setAttribute('label', feat[g_label])

            geometry.transform(xform)
            feat_i.setGeometry(geometry)
            features.append(feat_i)
            i += 1

        # Stop the algorithm if cancel button has been clicked
        if feedback.isCanceled():
            return {self.MAN_HOLES: 0}

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

        feedback.pushInfo('{} manholes have been imported'.format(i))
        return {self.MAN_HOLES: i}

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
