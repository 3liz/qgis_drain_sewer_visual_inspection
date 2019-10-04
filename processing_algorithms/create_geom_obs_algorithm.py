"""Create observations geometries."""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsFeature,
    QgsFeatureRequest,
    QgsExpression,
    QgsExpressionContext,
    QgsExpressionContextUtils,
)
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterVectorLayer,
    QgsProcessingOutputNumber,
    QgsProcessingException,
)

from ..qgis_plugin_tools.tools.fields import provider_fields

__copyright__ = 'Copyright 2019, 3Liz'
__license__ = 'GPL version 3'
__email__ = 'info@3liz.org'
__revision__ = '$Format:%H$'


class CreateGeomObsAlgorithm(QgsProcessingAlgorithm):
    SEGMENTS_TABLE = 'SEGMENTS_TABLE'
    GEOM_SEGMENTS = 'GEOM_SEGMENTS'
    OBSERVATION_TABLE = 'OBSERVATION_TABLE'
    GEOM_OBSERVATION = 'GEOM_OBSERVATION'

    OBSERVATIONS_CREATED = 'OBSERVATIONS_CREATED'

    def initAlgorithm(self, config):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.SEGMENTS_TABLE,
                self.tr('Tableau des tronçons d\'ITV'),
                [QgsProcessing.TypeVector]
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.GEOM_SEGMENTS,
                self.tr('Couche des géométries de tronçons'),
                [QgsProcessing.TypeVectorLine]
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.OBSERVATION_TABLE,
                self.tr('Tableau des observations'),
                [QgsProcessing.TypeVector]
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.GEOM_OBSERVATION,
                self.tr('Couche des géométries d\'observations'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        self.addOutput(QgsProcessingOutputNumber(self.OBSERVATIONS_CREATED, self.tr('Succès')))

    def processAlgorithm(self, parameters, context, feedback):

        t_troncon = self.parameterAsSource(parameters, self.SEGMENTS_TABLE, context)
        g_troncon = self.parameterAsSource(parameters, self.GEOM_SEGMENTS, context)
        t_obs = self.parameterAsSource(parameters, self.OBSERVATION_TABLE, context)
        g_obs = self.parameterAsVectorLayer(parameters, self.GEOM_OBSERVATION, context)

        # Get troncon ids and file ids
        exp_context = QgsExpressionContext()
        exp_context.appendScope(QgsExpressionContextUtils.globalScope())
        exp_context.appendScope(QgsExpressionContextUtils.projectScope(context.project()))
        exp_context.appendScope(t_troncon.createExpressionContextScope())

        exp_str = '"id_geom_troncon" IS NOT NULL'
        exp = QgsExpression(exp_str)

        exp.prepare(exp_context)
        if exp.hasEvalError():
            raise QgsProcessingException(
                self.tr('* ERROR: Expression %s has eval error: %s') % (exp.expression(), exp.evalErrorString()))

        request = QgsFeatureRequest(exp, exp_context)
        request.setSubsetOfAttributes(['id', 'aab', 'aad', 'aaf', 'abq', 'id_file', 'id_geom_troncon'], t_troncon.fields())
        has_geo_troncon = False
        troncons = {}
        file_ids = []
        for t in t_troncon.getFeatures(request):
            troncons[t['id']] = t
            file_ids.append(t['id_file'])
            has_geo_troncon = True

            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                return {self.OBSERVATIONS_CREATED: None}

        if not has_geo_troncon:
            raise QgsProcessingException(
                self.tr('* ERROR: No troncon geometries'))

        # Get observation ids
        exp_context = QgsExpressionContext()
        exp_context.appendScope(QgsExpressionContextUtils.globalScope())
        exp_context.appendScope(QgsExpressionContextUtils.projectScope(context.project()))
        exp_context.appendScope(t_obs.createExpressionContextScope())

        exp_str = '"id_troncon" IN (%s)' % ','.join([str(i) for i in troncons.keys()])
        exp_str += ' AND "id_file" IN (%s)' % ','.join([str(i) for i in file_ids])
        exp = QgsExpression(exp_str)

        exp.prepare(exp_context)
        if exp.hasEvalError():
            raise QgsProcessingException(
                self.tr('* ERROR: Expression %s has eval error: %s') % (exp.expression(), exp.evalErrorString()))

        obs_ids = []
        request = QgsFeatureRequest(exp, exp_context)
        for obs in t_obs.getFeatures(request):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                return {self.OBSERVATIONS_CREATED: None}

            troncon = troncons[obs['id_troncon']]

            # verifying ITV file
            if troncon['id_file'] != obs['id_file']:
                continue

            obs_ids.append(obs['id'])

        if not obs_ids:
            raise QgsProcessingException(
                self.tr('* ERROR: No observations to geolocalize found'))

        # Check observations already geolocalised on troncon
        exp_context = QgsExpressionContext()
        exp_context.appendScope(QgsExpressionContextUtils.globalScope())
        exp_context.appendScope(QgsExpressionContextUtils.projectScope(context.project()))
        exp_context.appendScope(QgsExpressionContextUtils.layerScope(g_obs))

        exp_str = '"id" IN (%s)' % ','.join([str(i) for i in obs_ids])
        exp = QgsExpression(exp_str)

        exp.prepare(exp_context)
        if exp.hasEvalError():
            raise QgsProcessingException(
                self.tr('* ERROR: Expression %s has eval error: %s') % (exp.expression(), exp.evalErrorString()))

        request = QgsFeatureRequest(exp, exp_context)
        geo_observations = []
        for g in g_obs.getFeatures(request):
            geo_observations.append(g['id'])

            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                return {self.OBSERVATIONS_CREATED: None}

        # build observation geometry based on table
        exp_context = QgsExpressionContext()
        exp_context.appendScope(QgsExpressionContextUtils.globalScope())
        exp_context.appendScope(QgsExpressionContextUtils.projectScope(context.project()))
        exp_context.appendScope(t_obs.createExpressionContextScope())

        exp_str = '"id_troncon" IN (%s)' % ','.join([str(i) for i in troncons.keys()])
        exp_str += ' AND "id_file" IN (%s)' % ','.join([str(i) for i in file_ids])
        if geo_observations:
            exp_str += ' AND id NOT IN (%s)' % ','.join([str(i) for i in geo_observations])
        exp = QgsExpression(exp_str)

        exp.prepare(exp_context)
        if exp.hasEvalError():
            raise QgsProcessingException(
                self.tr('* ERROR: Expression %s has eval error: %s') % (exp.expression(), exp.evalErrorString()))

        request = QgsFeatureRequest(exp, exp_context)
        features = []
        fields = provider_fields(g_obs.fields())
        for obs in t_obs.getFeatures(request):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                return {self.OBSERVATIONS_CREATED: None}

            troncon = troncons[obs['id_troncon']]

            # verifying ITV file
            if troncon['id_file'] != obs['id_file']:
                continue

            geo_req = QgsFeatureRequest()
            geo_req.setFilterFid(troncon['id_geom_troncon'])
            for g in g_troncon.getFeatures(geo_req):
                # Stop the algorithm if cancel button has been clicked
                if feedback.isCanceled():
                    return {self.OBSERVATIONS_CREATED: None}

                geom = g.geometry()
                pt = None
                if troncon['aab'] == troncon['aad']:
                    pt = geom.interpolate(geom.length() * obs['i'] / troncon['abq'])
                else:
                    pt = geom.interpolate(geom.length() * (1 - obs['i'] / troncon['abq']))
                fet = QgsFeature(fields)
                fet.setGeometry(pt)
                fet.setAttribute('id', obs['id'])
                features.append(fet)

        # Ajout des objets observations
        if features:
            g_obs.startEditing()
            (res, outFeats) = g_obs.dataProvider().addFeatures(features)
            if not res or not outFeats:
                raise QgsProcessingException(
                    self.tr('* ERREUR: lors de l\'enregistrement des regards %s') % ', '.join(g_obs.dataProvider().errors()))
            if not g_obs.commitChanges():
                raise QgsProcessingException(
                    self.tr('* ERROR: Commit %s.') % g_obs.commitErrors())

        # Returns empty dict if no outputs
        return {self.OBSERVATIONS_CREATED: len(features)}

    def name(self):
        return 'create_geom_obs'

    def displayName(self):
        return self.tr('10 Create observations geometries')

    def group(self):
        return self.tr('Drain Sewer Visual Inspection data')

    def groupId(self):
        return 'dsvi'

    @staticmethod
    def tr(string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return self.__class__()
