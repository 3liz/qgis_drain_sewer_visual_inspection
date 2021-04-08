"""Import DSVI/ITV files algorithm."""

import csv
import hashlib
import io
import os.path

from qgis.core import (QgsExpression, QgsExpressionContext,
                       QgsExpressionContextUtils, QgsFeatureRequest, QgsField,
                       QgsProcessing, QgsProcessingAlgorithm,
                       QgsProcessingException, QgsProcessingOutputNumber,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterVectorLayer, QgsVectorLayerUtils,
                       edit)
from qgis.PyQt.QtCore import QVariant

from ..qgis_plugin_tools.tools.fields import provider_fields
from ..qgis_plugin_tools.tools.i18n import tr

__copyright__ = 'Copyright 2019, 3Liz'
__license__ = 'GPL version 3'
__email__ = 'info@3liz.org'
__revision__ = '$Format:%H$'


class ImportDsviFileAlgorithm(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    FILE_TABLE = 'FILE_TABLE'
    SEGMENT_TABLE = 'SEGMENT_TABLE'
    OBSERVATIONS_TABLE = 'OBSERVATIONS_TABLE'
    MANHOLES_TABLE = 'MANHOLES_TABLE'

    SUCCESS = 'SUCCESS'

    def initAlgorithm(self, config):
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT,
                tr('Fichier d\'ITV')
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.FILE_TABLE,
                tr('Tableau des fichiers d\'ITV importés'),
                [QgsProcessing.TypeVector],
                defaultValue='file'
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.SEGMENT_TABLE,
                tr('Tableau des tronçons d\'ITV'),
                [QgsProcessing.TypeVector],
                defaultValue='troncon'
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.OBSERVATIONS_TABLE,
                tr('Tableau des observations d\'ITV'),
                [QgsProcessing.TypeVector],
                defaultValue='obs'
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.MANHOLES_TABLE,
                tr('Tableau des regards d\'ITV'),
                [QgsProcessing.TypeVector],
                defaultValue='regard'
            )
        )

        self.addOutput(
            QgsProcessingOutputNumber(
                self.SUCCESS,
                tr('Succès')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        path = self.parameterAsFile(parameters, self.INPUT, context)
        t_file = self.parameterAsVectorLayer(
            parameters,
            self.FILE_TABLE,
            context
        )
        t_troncon = self.parameterAsVectorLayer(
            parameters,
            self.SEGMENT_TABLE,
            context
        )
        t_obs = self.parameterAsVectorLayer(
            parameters,
            self.OBSERVATIONS_TABLE,
            context
        )
        t_regard = self.parameterAsVectorLayer(
            parameters,
            self.MANHOLES_TABLE,
            context
        )

        paths = path.split(';')
        if len(paths) != 1:
            raise QgsProcessingException(
                tr('* ERREUR: 1 fichier a la fois {}.').format(path)
            )

        if not os.path.exists(path):
            raise QgsProcessingException(
                tr('* ERREUR: {} n\'existe pas.').format(path)
            )

        # add date fields to itv file table
        # relation_aggregate(
        #     'itv_tronco_id_file_itv_file20_id',
        #     'max',
        #     "abf"
        # )
        if 'date_debut' not in t_file.dataProvider().fields().names():
            with edit(t_file):
                res = t_file.dataProvider().addAttributes([
                    QgsField("date_debut", QVariant.String),
                    QgsField("date_fin", QVariant.String)
                ])
                if res:
                    t_file.updateFields()

        feat_file = None
        with open(path, 'rb') as f:
            basename = os.path.basename(path)
            md = hashlib.md5()
            md.update(f.read())
            hashcontent = md.hexdigest()

            feat_file = QgsVectorLayerUtils.createFeature(t_file)
            feat_file.setAttribute('basename', basename)
            feat_file.setAttribute('hashcontent', hashcontent)

        if not feat_file:
            raise QgsProcessingException(
                tr(
                    '* ERREUR: le fichier {} n\'a pas été lu '
                    'correctement.'
                ).format(path)
            )

        exp_context = QgsExpressionContext()
        exp_context.appendScope(
            QgsExpressionContextUtils.globalScope()
        )
        exp_context.appendScope(
            QgsExpressionContextUtils.projectScope(context.project())
        )
        exp_context.appendScope(
            QgsExpressionContextUtils.layerScope(t_file)
        )

        exp_str = QgsExpression.createFieldEqualityExpression(
            'basename', feat_file['basename']
        ) + ' AND ' + QgsExpression.createFieldEqualityExpression(
            'hashcontent', feat_file['hashcontent']
        )
        exp = QgsExpression(exp_str)

        exp.prepare(exp_context)
        if exp.hasEvalError():
            raise QgsProcessingException(
                tr('* ERROR: Expression {} has eval error: {}').format(
                    exp.expression(), exp.evalErrorString()
                )
            )

        request = QgsFeatureRequest(exp, exp_context)
        request.setLimit(1)

        for _t in t_file.getFeatures(request):
            raise QgsProcessingException(
                tr('* ERREUR: le fichier {} a deja ete lu').format(
                    path
                )
            )

        exp_str = QgsExpression.createFieldEqualityExpression(
            'hashcontent', feat_file['hashcontent']
        )
        exp = QgsExpression(exp_str)

        exp.prepare(exp_context)
        if exp.hasEvalError():
            raise QgsProcessingException(
                tr('* ERROR: Expression {} has eval error: {}').format(
                    (exp.expression(), exp.evalErrorString())
                )
            )

        request = QgsFeatureRequest(exp, exp_context)
        request.setLimit(1)

        for _t in t_file.getFeatures(request):
            raise QgsProcessingException(
                tr(
                    '* ERREUR: le fichier {} semble deja avoir ete lu'
                ).format(path)
            )

        exp_context = QgsExpressionContext()
        exp_context.appendScope(
            QgsExpressionContextUtils.globalScope()
        )
        exp_context.appendScope(
            QgsExpressionContextUtils.projectScope(context.project())
        )
        exp_context.appendScope(
            QgsExpressionContextUtils.layerScope(t_troncon)
        )

        exp_str = 'maximum("id")'
        exp = QgsExpression(exp_str)

        exp.prepare(exp_context)
        if exp.hasEvalError():
            raise QgsProcessingException(
                tr(
                    '* ERROR: Expression {} has eval error: {}'
                ).format(exp.expression(), exp.evalErrorString())
            )

        last_t_id = exp.evaluate(exp_context)
        if not last_t_id:
            last_t_id = 0

        exp_context = QgsExpressionContext()
        exp_context.appendScope(
            QgsExpressionContextUtils.globalScope()
        )
        exp_context.appendScope(
            QgsExpressionContextUtils.projectScope(context.project())
        )
        exp_context.appendScope(
            QgsExpressionContextUtils.layerScope(t_regard)
        )

        exp_str = 'maximum("id")'
        exp = QgsExpression(exp_str)

        exp.prepare(exp_context)
        if exp.hasEvalError():
            raise QgsProcessingException(
                tr(
                    '* ERROR: Expression {} has eval error: {}'
                ).format(exp.expression(), exp.evalErrorString())
            )

        last_r_id = exp.evaluate(exp_context)
        if not last_r_id:
            last_r_id = 0

        # lecture des entetes
        ENCODING = 'ISO-8859-1'
        LANG = 'fr'
        DELIMITER = ','
        DECIMAL = '.'
        QUOTECHAR = '"'
        VERSION = ''

        with open(path, 'rb') as f:
            for line in f:
                # Stop the algorithm if cancel button has been clicked
                if feedback.isCanceled():
                    return {self.SUCCESS: 0}
                try:
                    line = line.decode()
                except UnicodeDecodeError:
                    raise QgsProcessingException(
                        'Error while reading {}'.format(path)
                    )
                # remove break line
                line = line.replace('\n', '').replace('\r', '')
                if line.startswith('#'):
                    if line.startswith('#A'):
                        if line.startswith('#A1'):
                            ENCODING = line[4:]
                            if ENCODING.find(':') != -1:
                                ENCODING = ENCODING[:ENCODING.find(':')]
                        elif line.startswith('#A2'):
                            LANG = line[4:]
                        elif line.startswith('#A3'):
                            DELIMITER = line[4:]
                        elif line.startswith('#A4'):
                            DECIMAL = line[4:]
                        elif line.startswith('#A5'):
                            QUOTECHAR = line[4:]
                    else:
                        break

        # Dialect CSV pour la lecture des tableaux de valeurs du
        # fichier d'ITV
        class itvDialect(csv.Dialect):
            strict = True
            skipinitialspace = True
            quoting = csv.QUOTE_MINIMAL
            delimiter = DELIMITER
            quotechar = QUOTECHAR
            lineterminator = '\r\n'

        # Liste des troncons, observations et regards
        troncons = []
        regards = []
        observations = []

        # Lectures des donnees
        with open(path, 'rb') as f:
            # Identifiant de départ
            t_id = last_t_id
            r_id = last_r_id
            # Entête
            header = []
            # Nom du tableau
            array = ''
            # Observations de troncons ?
            obs_for_troncon = False
            # initialisation du Dialect CSV pour ITV
            dia = itvDialect()
            # Lecture ligne à ligne du fichier
            for line in f:
                # Stop the algorithm if cancel button has been clicked
                if feedback.isCanceled():
                    return {self.SUCCESS: 0}
                # Decoding line en utilisant l'encoding du fichier
                line = line.decode(ENCODING)
                # remove break line
                line = line.replace('\n', '').replace('\r', '')
                # Ligne commençant par un # est une ligne d'entête
                if line.startswith('#'):
                    # Entête de troncon ou regard
                    if line.startswith('#B'):
                        l_b = io.StringIO(line[5:])
                        for l_r in csv.reader(l_b, dia):
                            header = l_r
                            break
                        array = line[1:4]
                        continue
                    # Entête d'observation
                    elif line.startswith('#C'):
                        if header[0].startswith('A'):
                            obs_for_troncon = True
                        else:
                            obs_for_troncon = False
                        l_b = io.StringIO(line[3:])
                        for l_r in csv.reader(l_b, dia):
                            header = l_r
                            break
                        array = line[1:2]
                        continue
                    # Fin d'observation
                    elif line.startswith('#Z'):
                        header = []
                        array = ''
                        obs_for_troncon = False
                        continue
                # La ligne contient des donnees
                else:
                    if not header:  # an error in the file structure
                        continue
                    l_b = io.StringIO(line)
                    for l_r in csv.reader(l_b, dia):
                        data = l_r
                        row = list(
                            zip(
                                [h.lower() for h in header],
                                [t for t in data]
                            )
                        )
                        # observation
                        if array == 'C':
                            if obs_for_troncon:
                                observations.append(
                                    row + [('id_troncon', t_id)]
                                )
                        # Premiere ligne de description d'un troncon ou regard
                        elif array == 'B01':
                            if header[0].startswith('A'):
                                t_id += 1
                                troncons.append([('id', t_id)] + row)
                            elif header[0].startswith('C'):
                                r_id += 1
                                regards.append([('id', r_id)] + row)
                        # Ligne complémentaire de description
                        else:
                            if header[0].startswith('A'):
                                troncons[-1] += row
                            elif header[0].startswith('C'):
                                regards[-1] += row

        # Recuperation des references de noeuds et dates
        itv_dates = []
        regard_node_refs = []
        regard_ref_id = {}
        max_r_id = last_r_id
        for reg in regards:
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                return {self.SUCCESS: 0}

            d_rg = dict(reg)
            if d_rg['caa'] and d_rg['caa'] not in regard_node_refs:
                regard_node_refs.append(d_rg['caa'])
                regard_ref_id[d_rg['caa']] = d_rg['id']
            if d_rg['id'] and d_rg['id'] > max_r_id:
                max_r_id = d_rg['id']
            if 'cbf' in d_rg and d_rg['cbf'] not in itv_dates:
                itv_dates.append(d_rg['cbf'])

        node_refs = []
        for tro in troncons:
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                return {self.SUCCESS: 0}

            d_tr = dict(tro)
            if d_tr['aad'] and \
                    d_tr['aad'] not in regard_node_refs and \
                    d_tr['aad'] not in node_refs:
                node_refs.append(d_tr['aad'])
            if d_tr['aaf'] and \
                    d_tr['aaf'] not in regard_node_refs and \
                    d_tr['aaf'] not in node_refs:
                node_refs.append(d_tr['aaf'])
            if 'aat' in d_tr and \
                    d_tr['aat'] and \
                    d_tr['aat'] not in regard_node_refs and \
                    d_tr['aat'] not in node_refs:
                node_refs.append(d_tr['aat'])
            if 'abf' in d_tr and d_tr['abf'] not in itv_dates:
                itv_dates.append(d_tr['abf'])

        # Ajout des regards manquant
        for n_ref in node_refs:
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                return {self.SUCCESS: 0}

            max_r_id += 1
            regards.append([('id', max_r_id), ('caa', n_ref)])
            regard_ref_id[n_ref] = max_r_id

        # Ajout des identifiants de regards aux tronçons
        regard_refs = regard_ref_id.keys()
        for tro in troncons:
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                return {self.SUCCESS: 0}

            d_tr = dict(tro)
            if d_tr['aad'] and \
                    d_tr['aad'] in regard_refs:
                tro += [('id_regard1', regard_ref_id[d_tr['aad']])]
            if d_tr['aaf'] and \
                    d_tr['aaf'] in regard_refs:
                tro += [('id_regard2', regard_ref_id[d_tr['aaf']])]
            if 'aat' in d_tr.keys() and \
                    d_tr['aat'] and \
                    d_tr['aat'] in regard_refs:
                tro += [('id_regard3', regard_ref_id[d_tr['aat']])]

        # Verification des champs
        fields = provider_fields(t_troncon.fields())
        for tro in troncons:
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                return {self.SUCCESS: 0}

            for key, val in tro:
                # Stop the algorithm if cancel button has been clicked
                if feedback.isCanceled():
                    return {self.SUCCESS: 0}

                if fields.indexOf(key) == -1:
                    raise QgsProcessingException(
                        tr(
                            '* ERREUR dans le fichier : '
                            'le champs de tronçon "{}" est inconnue'
                        ).format(key)
                    )
                field = fields.field(key)
                if isinstance(val, str) and field.isNumeric():
                    if val:
                        try:
                            float(val.replace(DECIMAL, '.'))
                        except BaseException:
                            raise QgsProcessingException(
                                tr(
                                    '* ERREUR dans le fichier : '
                                    'le champs de tronçon "{}" est '
                                    'numérique mais pas la valeur "{}"'
                                ).format(key, val)
                            )

        fields = provider_fields(t_obs.fields())
        for obs in observations:
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                return {self.SUCCESS: 0}

            for key, val in obs:
                # Stop the algorithm if cancel button has been clicked
                if feedback.isCanceled():
                    return {self.SUCCESS: 0}

                if fields.indexOf(key) == -1:
                    raise QgsProcessingException(
                        tr(
                            '* ERREUR dans le fichier : '
                            'le champs d\'observation "{}" est '
                            'inconnue'
                        ).format(key)
                    )
                field = fields.field(key)
                if isinstance(val, str) and field.isNumeric():
                    if val:
                        try:
                            float(val.replace(DECIMAL, '.'))
                        except BaseException:
                            raise QgsProcessingException(
                                tr(
                                    '* ERREUR dans le fichier : '
                                    'le champs d\'observation "{}" est '
                                    'numérique mais pas la valeur "{}"'
                                ).format(key, val)
                            )

        fields = provider_fields(t_regard.fields())
        for reg in regards:
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                return {self.SUCCESS: 0}

            for key, val in reg:
                # Stop the algorithm if cancel button has been clicked
                if feedback.isCanceled():
                    return {self.SUCCESS: 0}

                if fields.indexOf(key) == -1:
                    raise QgsProcessingException(
                        tr(
                            '* ERREUR dans le fichier : '
                            'le champs de regard "{}" est inconnue'
                        ).format(key)
                    )
                field = fields.field(key)
                if isinstance(val, str) and field.isNumeric():
                    if val:
                        try:
                            float(val.replace(DECIMAL, '.'))
                        except BaseException:
                            raise QgsProcessingException(
                                tr(
                                    '* ERREUR dans le fichier : '
                                    'le champs de regard "{}" est '
                                    'numérique mais pas la valeur "{}"'
                                ).format(key, val)
                            )

        # Finalisation objet fichier
        feat_file.setAttribute('encoding', ENCODING)
        feat_file.setAttribute('lang', LANG)
        if VERSION:
            feat_file.setAttribute('version', VERSION)
        if itv_dates:
            feat_file.setAttribute('date_debut', min(itv_dates))
            feat_file.setAttribute('date_fin', max(itv_dates))

        # Stop the algorithm if cancel button has been clicked
        if feedback.isCanceled():
            return {self.SUCCESS: 0}

        # Ajout de l'objet fichier
        t_file.startEditing()
        (res, outFeats) = t_file.dataProvider().addFeatures([feat_file])
        if not res or not outFeats:
            raise QgsProcessingException(
                tr(
                    '* ERREUR: lors de l\'enregistrement du fichier {}'
                ).format(', '.join(t_file.dataProvider().errors()))
            )
        if not t_file.commitChanges():
            raise QgsProcessingException(
                tr('* ERROR: Commit {}.').format(t_file.commitErrors())
            )

        # Mise a jour de l'identifiant de l'objet fichier
        feat_file.setAttribute('id', outFeats[0]['id'])

        # Creation des objets troncons
        features = []
        fields = provider_fields(t_troncon.fields())
        for tro in troncons:
            feat_t = QgsVectorLayerUtils.createFeature(t_troncon)
            feat_t.setAttribute('id_file', feat_file['id'])
            for key, val in tro:
                field = fields.field(key)
                if isinstance(val, str) and field.isNumeric():
                    if val:
                        feat_t.setAttribute(
                            key, float(val.replace(DECIMAL, '.'))
                        )
                else:
                    feat_t.setAttribute(key, val)
            features.append(feat_t)

        # Ajout des objets troncons
        if features:
            t_troncon.startEditing()
            (res, outFeats) = t_troncon.dataProvider().addFeatures(features)
            if not res or not outFeats:
                raise QgsProcessingException(
                    tr(
                        '* ERREUR: lors de l\'enregistrement '
                        'des troncon {}'
                    ).format(
                        ', '.join(t_troncon.dataProvider().errors())
                    )
                )
            if not t_troncon.commitChanges():
                raise QgsProcessingException(
                    tr('* ERROR: Commit {}.').format(
                        t_troncon.commitErrors()
                    )
                )

        # Creation des objets observations
        features = []
        fields = provider_fields(t_obs.fields())
        for obs in observations:
            feat_o = QgsVectorLayerUtils.createFeature(t_obs)
            feat_o.setAttribute('id_file', feat_file['id'])
            for key, val in obs:
                field = fields.field(key)
                if isinstance(val, str) and field.isNumeric():
                    if val:
                        feat_o.setAttribute(
                            key, float(val.replace(DECIMAL, '.'))
                        )
                else:
                    feat_o.setAttribute(key, val)
            features.append(feat_o)

        # Ajout des objets observations
        if features:
            t_obs.startEditing()
            (res, outFeats) = t_obs.dataProvider().addFeatures(features)
            if not res or not outFeats:
                raise QgsProcessingException(
                    tr(
                        '* ERREUR: lors de l\'enregistrement '
                        'des observations {}'
                    ).format(
                        ', '.join(t_obs.dataProvider().errors())
                    )
                )
            if not t_obs.commitChanges():
                raise QgsProcessingException(
                    tr('* ERROR: Commit {}.').format(
                        t_obs.commitErrors()
                    )
                )

        # Creation des objets regards
        features = []
        fields = provider_fields(t_regard.fields())
        for reg in regards:
            feat_r = QgsVectorLayerUtils.createFeature(t_regard)
            feat_r.setAttribute('id_file', feat_file['id'])
            for key, val in reg:
                field = fields.field(key)
                if isinstance(val, str) and field.isNumeric():
                    if val:
                        feat_r.setAttribute(
                            key, float(val.replace(DECIMAL, '.'))
                        )
                else:
                    feat_r.setAttribute(key, val)
            features.append(feat_r)

        # Ajout des objets regards
        if features:
            t_regard.startEditing()
            (res, outFeats) = t_regard.dataProvider().addFeatures(
                features
            )
            if not res or not outFeats:
                raise QgsProcessingException(
                    tr(
                        '* ERREUR: lors de l\'enregistrement '
                        'des regards {}'
                    ).format(
                        ', '.join(t_regard.dataProvider().errors())
                    )
                )
            if not t_regard.commitChanges():
                raise QgsProcessingException(
                    tr('* ERROR: Commit %s.').format(
                        t_regard.commitErrors()
                    )
                )

        # Returns empty dict if no outputs
        return {self.SUCCESS: 1}

    def shortHelpString(self) -> str:
        return tr(
            'It will import Drain Sewer Visual Inspection data '
            'into the geopackage.'
        )

    def name(self):
        return 'import_dsvi_data'

    def displayName(self):
        return '{} {}'.format('00', tr('Import DSVI data'))

    def group(self):
        return tr('Drain Sewer Visual Inspection data')

    def groupId(self):
        return 'dsvi'

    def createInstance(self):
        return self.__class__()
