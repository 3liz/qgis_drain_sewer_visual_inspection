"""Create geom segment algorithm."""

from qgis.core import (QgsExpression, QgsExpressionContext,
                       QgsExpressionContextUtils, QgsFeatureRequest,
                       QgsGeometry, QgsProcessing, QgsProcessingAlgorithm,
                       QgsProcessingException, QgsProcessingOutputNumber,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterVectorLayer, QgsVectorLayerUtils)

from ..qgis_plugin_tools.tools.i18n import tr

__copyright__ = 'Copyright 2019, 3Liz'
__license__ = 'GPL version 3'
__email__ = 'info@3liz.org'
__revision__ = '$Format:%H$'


class CreateGeomTronconAlgorithm(QgsProcessingAlgorithm):
    MANHOLES_TABLE = 'MANHOLES_TABLE'
    GEOM_MANHOLES = 'GEOM_MANHOLES'
    SEGMENTS_TABLE = 'SEGMENTS_TABLE'
    GEOM_SEGMENTS = 'GEOM_SEGMENTS'

    SEGMENT_CREATED = 'SEGMENT_CREATED'

    def initAlgorithm(self, config):

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.MANHOLES_TABLE,
                tr('Tableau des regards d\'ITV'),
                [QgsProcessing.TypeVector],
                defaultValue='regard'
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.GEOM_MANHOLES,
                tr('Couche des géométries de regards'),
                [QgsProcessing.TypeVectorPoint],
                defaultValue='geom_regard'
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.SEGMENTS_TABLE,
                tr('Tableau des tronçons d\'ITV'),
                [QgsProcessing.TypeVector],
                defaultValue='troncon'
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.GEOM_SEGMENTS,
                tr('Couche des géométries de tronçons'),
                [QgsProcessing.TypeVectorLine],
                defaultValue='geom_troncon'
            )
        )

        self.addOutput(QgsProcessingOutputNumber(self.SEGMENT_CREATED, tr('Number of segment created')))

    def processAlgorithm(self, parameters, context, feedback):

        t_regard = self.parameterAsSource(parameters, self.MANHOLES_TABLE, context)
        g_regard = self.parameterAsSource(parameters, self.GEOM_MANHOLES, context)
        t_troncon = self.parameterAsVectorLayer(parameters, self.SEGMENTS_TABLE, context)
        g_troncon = self.parameterAsVectorLayer(parameters, self.GEOM_SEGMENTS, context)

        exp_context = QgsExpressionContext()
        exp_context.appendScope(QgsExpressionContextUtils.globalScope())
        exp_context.appendScope(QgsExpressionContextUtils.projectScope(context.project()))
        exp_context.appendScope(QgsExpressionContextUtils.layerScope(t_troncon))

        exp_str = '"id_geom_troncon" IS NULL'
        exp = QgsExpression(exp_str)

        exp.prepare(exp_context)
        if exp.hasEvalError():
            raise QgsProcessingException(
                tr('* ERROR: Expression %s has eval error: %s') % (exp.expression(), exp.evalErrorString()))

        request = QgsFeatureRequest(exp, exp_context)
        r_ids = []  # identifiant des regards
        l_t_f = {}  # lien troncon fichier
        l_f_t = {}  # lien fichier troncons
        troncons = {}
        sorties = {}
        entrees = {}
        for t in t_troncon.getFeatures(request):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                return {self.SEGMENT_CREATED: None}

            segment_number = t['id']
            r1 = t['id_regard1']
            r2 = t['id_regard2']

            if r1 not in r_ids:
                r_ids.append(r1)
            if r2 not in r_ids:
                r_ids.append(r2)

            fid = t['id_file']
            l_t_f[segment_number] = fid
            if fid in l_f_t:
                l_f_t[fid] = l_f_t[fid] + [segment_number]
            else:
                l_f_t[fid] = [segment_number]

            troncons[segment_number] = (r1, r2)
            if r1 in sorties:
                sorties[r1] = sorties[r1] + [segment_number]
            else:
                sorties[r1] = [segment_number]
            if r2 in entrees:
                entrees[r2] = entrees[r2] + [segment_number]
            else:
                entrees[r2] = [segment_number]

        exp_context = QgsExpressionContext()
        exp_context.appendScope(QgsExpressionContextUtils.globalScope())
        exp_context.appendScope(QgsExpressionContextUtils.projectScope(context.project()))
        exp_context.appendScope(t_regard.createExpressionContextScope())

        exp_str = '"id_geom_regard" IS NOT NULL AND "id" IN (%s)' % ','.join([str(i) for i in r_ids] + ['-1'])
        exp = QgsExpression(exp_str)

        exp.prepare(exp_context)
        if exp.hasEvalError():
            raise QgsProcessingException(
                tr('* ERROR: Expression %s has eval error: %s') % (exp.expression(), exp.evalErrorString()))

        request = QgsFeatureRequest(exp, exp_context)
        g_ids = []  # identifiants des géométrie de regards
        l_r_g = {}  # lien regard geometrie
        l_g_r = {}  # lien geometrie regards
        for t in t_regard.getFeatures(request):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                return {self.SEGMENT_CREATED: None}

            segment_number = t['id']
            fid = t['id_file']

            if segment_number in sorties:
                sorties[segment_number] = [trid for trid in sorties[segment_number] if l_t_f[trid] == fid]
            if segment_number in entrees:
                entrees[segment_number] = [trid for trid in entrees[segment_number] if l_t_f[trid] == fid]

            gid = t['id_geom_regard']
            l_r_g[segment_number] = gid
            if gid not in g_ids:
                g_ids.append(gid)
            if gid in l_g_r:
                l_g_r[gid] = l_g_r[gid] + [segment_number]
            else:
                l_g_r[gid] = [segment_number]

        exp_context = QgsExpressionContext()
        exp_context.appendScope(QgsExpressionContextUtils.globalScope())
        exp_context.appendScope(QgsExpressionContextUtils.projectScope(context.project()))
        exp_context.appendScope(g_regard.createExpressionContextScope())

        exp_str = '"id" IN (%s)' % ','.join([str(i) for i in g_ids] + ['-1'])
        exp = QgsExpression(exp_str)

        exp.prepare(exp_context)
        if exp.hasEvalError():
            raise QgsProcessingException(
                tr('* ERROR: Expression %s has eval error: %s') % (exp.expression(), exp.evalErrorString()))

        request = QgsFeatureRequest(exp, exp_context)
        points = {}
        pt_labels = {}
        for g in g_regard.getFeatures(request):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                return {self.SEGMENT_CREATED: None}

            segment_number = g['id']
            points[segment_number] = g.geometry().asPoint()
            pt_labels[segment_number] = g['label']

        lines = {}
        for gid in points:
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                return {self.SEGMENT_CREATED: None}

            if gid not in l_g_r:
                continue

            for rid in l_g_r[gid]:
                # Stop the algorithm if cancel button has been clicked
                if feedback.isCanceled():
                    return {self.SEGMENT_CREATED: None}

                if rid in sorties:
                    for tid in sorties[rid]:
                        # Stop the algorithm if cancel button has been clicked
                        if feedback.isCanceled():
                            return {self.SEGMENT_CREATED: None}

                        if tid in lines:
                            continue
                        if tid not in troncons:
                            continue
                        r2 = troncons[tid][1]
                        if r2 not in l_r_g:
                            continue
                        g2 = l_r_g[r2]
                        if g2 not in points:
                            continue
                        lines[tid] = (gid, g2)

                if rid in entrees:
                    for tid in entrees[rid]:
                        # Stop the algorithm if cancel button has been clicked
                        if feedback.isCanceled():
                            return {self.SEGMENT_CREATED: None}

                        if tid in lines:
                            continue
                        if tid not in troncons:
                            continue
                        r1 = troncons[tid][0]
                        if r1 not in l_r_g:
                            continue
                        g1 = l_r_g[r1]
                        if g1 not in points:
                            continue
                        lines[tid] = (g1, gid)

        # Creation des troncons
        l_t_g = {}  # lien troncon et geometrie troncon
        l_pts_t = {}  # lien points troncons
        features = []  # les objets de geometrie de troncon
        geom_point_keys = []  # liste des clés des points troncons
        for tid, pts in lines.items():
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                return {self.SEGMENT_CREATED: None}

            exp_context = QgsExpressionContext()
            exp_context.appendScope(QgsExpressionContextUtils.globalScope())
            exp_context.appendScope(QgsExpressionContextUtils.projectScope(context.project()))
            exp_context.appendScope(QgsExpressionContextUtils.layerScope(g_troncon))

            exp_str = '"id_geom_regard_amont" = %s AND "id_geom_regard_aval" = %s' % pts
            exp = QgsExpression(exp_str)

            exp.prepare(exp_context)
            if exp.hasEvalError():
                raise QgsProcessingException(
                    tr('* ERROR: Expression %s has eval error: %s') % (exp.expression(), exp.evalErrorString()))

            request = QgsFeatureRequest(exp, exp_context)
            request.setLimit(1)
            for g in g_troncon.getFeatures(request):
                l_t_g[tid] = g['id']
                continue

            if (pts[0], pts[1]) in geom_point_keys:
                l_pts_t[(pts[0], pts[1])].append(tid)
                continue
            else:
                l_pts_t[(pts[0], pts[1])] = [tid]
                geom_point_keys.append((pts[0], pts[1]))

            feat_t = QgsVectorLayerUtils.createFeature(g_troncon)
            feat_t.setAttribute('label', str(pt_labels[pts[0]]) + '-' + str(pt_labels[pts[1]]))
            feat_t.setAttribute('id_geom_regard_amont', pts[0])
            feat_t.setAttribute('id_geom_regard_aval', pts[1])
            feat_t.setGeometry(QgsGeometry.fromPolylineXY([points[pts[0]], points[pts[1]]]))
            features.append(feat_t)

        # Ajout des objets troncons
        if features:
            g_troncon.startEditing()
            (res, outFeats) = g_troncon.dataProvider().addFeatures(features)
            if not res or not outFeats:
                raise QgsProcessingException(
                    tr('* ERREUR: lors de l\'enregistrement des regards %s') % ', '.join(g_troncon.dataProvider().errors()))
            if not g_troncon.commitChanges():
                raise QgsProcessingException(
                    tr('* ERROR: Commit %s.') % g_troncon.commitErrors())

            for g in outFeats:
                # Stop the algorithm if cancel button has been clicked
                if feedback.isCanceled():
                    return {self.SEGMENT_CREATED: None}

                if not g['id']:
                    continue
                key = (g['id_geom_regard_amont'], g['id_geom_regard_aval'])
                if key not in geom_point_keys:
                    continue
                for tid in l_pts_t[(pts[0], pts[1])]:
                    l_t_g[tid] = g['id']
                    # Stop the algorithm if cancel button has been clicked
                    if feedback.isCanceled():
                        return {self.SEGMENT_CREATED: None}

        for tid, pts in lines.items():
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                return {self.SEGMENT_CREATED: None}

            if tid in l_t_g:
                continue
            exp_context = QgsExpressionContext()
            exp_context.appendScope(QgsExpressionContextUtils.globalScope())
            exp_context.appendScope(QgsExpressionContextUtils.projectScope(context.project()))
            exp_context.appendScope(QgsExpressionContextUtils.layerScope(g_troncon))

            exp_str = '"id_geom_regard_amont" = %s AND "id_geom_regard_aval" = %s' % pts
            exp = QgsExpression(exp_str)

            exp.prepare(exp_context)
            if exp.hasEvalError():
                raise QgsProcessingException(
                    tr('* ERROR: Expression %s has eval error: %s') % (exp.expression(), exp.evalErrorString()))

            request = QgsFeatureRequest(exp, exp_context)
            request.setLimit(1)
            for g in g_troncon.getFeatures(request):
                l_t_g[tid] = g['id']
                # Stop the algorithm if cancel button has been clicked
                if feedback.isCanceled():
                    return {self.SEGMENT_CREATED: None}

        if not l_t_g.keys():
            raise QgsProcessingException(
                tr('* ERREUR: Aucune géométrie de tronçon'))

        # Mise a jour de la table troncon
        exp_context = QgsExpressionContext()
        exp_context.appendScope(QgsExpressionContextUtils.globalScope())
        exp_context.appendScope(QgsExpressionContextUtils.projectScope(context.project()))
        exp_context.appendScope(QgsExpressionContextUtils.layerScope(t_troncon))

        exp_str = '"id_geom_troncon" IS NULL AND id IN (%s)' % ','.join([str(i) for i in l_t_g.keys()])
        exp = QgsExpression(exp_str)

        exp.prepare(exp_context)
        if exp.hasEvalError():
            raise QgsProcessingException(
                tr('* ERROR: Expression %s has eval error: %s') % (exp.expression(), exp.evalErrorString()))

        # Mise a jour de la table de tronçon
        request = QgsFeatureRequest(exp, exp_context)
        t_troncon.startEditing()
        segment_number = 0
        for t in t_troncon.getFeatures(request):
            t.setAttribute('id_geom_troncon', l_t_g[t['id']])
            t_troncon.updateFeature(t)
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                return {self.SEGMENT_CREATED: None}
            segment_number += 1

        if not t_troncon.commitChanges():
            raise QgsProcessingException(
                tr('* ERROR: Commit %s.') % t_troncon.commitErrors())

        # Returns empty dict if no outputs
        return {self.SEGMENT_CREATED: segment_number}

    def shortHelpString(self) -> str:
        return tr('Generate segments from manholes.')

    def name(self):
        return 'create_geom_segment'

    def displayName(self):
        return '{} {}'.format('05', tr('Create segment geometries'))

    def group(self):
        return tr('Drain Sewer Visual Inspection data')

    def groupId(self):
        return 'dsvi'

    def createInstance(self):
        return self.__class__()
