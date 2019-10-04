"""Import DSVI/ITV files algorithm."""

import csv
import hashlib
import io
import os.path

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFile,
    QgsProcessingParameterVectorLayer,
    QgsProcessingOutputNumber,
    QgsProcessingException,
)
from qgis.core import (
    edit,
    QgsFeature,
    QgsField,
    QgsFeatureRequest,
    QgsExpression,
    QgsExpressionContext,
    QgsExpressionContextUtils,
)

from ..qgis_plugin_tools.tools.fields import provider_fields

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
                self.tr('Fichier d\'ITV')
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.FILE_TABLE,
                self.tr('Tableau des fichiers d\'ITV importés'),
                [QgsProcessing.TypeVector]
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.SEGMENT_TABLE,
                self.tr('Tableau des tronçons d\'ITV'),
                [QgsProcessing.TypeVector]
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.OBSERVATIONS_TABLE,
                self.tr('Tableau des observations d\'ITV'),
                [QgsProcessing.TypeVector]
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.MANHOLES_TABLE,
                self.tr('Tableau des regards d\'ITV'),
                [QgsProcessing.TypeVector]
            )
        )

        self.addOutput(QgsProcessingOutputNumber(self.SUCCESS, self.tr('Succès')))

    def processAlgorithm(self, parameters, context, feedback):
        path = self.parameterAsFile(parameters, self.INPUT, context)
        t_file = self.parameterAsVectorLayer(parameters, self.FILE_TABLE, context)
        t_troncon = self.parameterAsVectorLayer(parameters, self.SEGMENT_TABLE, context)
        t_obs = self.parameterAsVectorLayer(parameters, self.OBSERVATIONS_TABLE, context)
        t_regard = self.parameterAsVectorLayer(parameters, self.MANHOLES_TABLE, context)

        paths = path.split(';')
        if len(paths) != 1:
            raise QgsProcessingException(
                self.tr('* ERREUR: 1 fichier a la fois %s.') % path)

        if not os.path.exists(path):
            raise QgsProcessingException(
                self.tr('* ERREUR: %s n\'existe pas.') % path)

        # add date fields to itv file table
        # relation_aggregate( 'itv_tronco_id_file_itv_file20_id', 'max', "abf")
        if 'date_debut' not in t_file.dataProvider().fields().names():
            with edit(t_file):
                res = t_file.dataProvider().addAttributes(
                    [QgsField("date_debut", QVariant.String),
                     QgsField("date_fin", QVariant.String)])
                if res:
                    t_file.updateFields()

        feat_file = None
        with open(path, 'rb') as f:
            basename = os.path.basename(path)
            m = hashlib.md5()
            m.update(f.read())
            hashcontent = m.hexdigest()

            feat_file = QgsFeature(provider_fields(t_file.fields()))
            feat_file.setAttribute('basename', basename)
            feat_file.setAttribute('hashcontent', hashcontent)

        if not feat_file:
            raise QgsProcessingException(
                self.tr('* ERREUR: le fichier %s n\'a pas ete lu correctement.') % path)

        exp_context = QgsExpressionContext()
        exp_context.appendScope(QgsExpressionContextUtils.globalScope())
        exp_context.appendScope(QgsExpressionContextUtils.projectScope(context.project()))
        exp_context.appendScope(QgsExpressionContextUtils.layerScope(t_file))

        exp_str = QgsExpression.createFieldEqualityExpression('basename', feat_file['basename']) + ' AND ' + \
                  QgsExpression.createFieldEqualityExpression('hashcontent', feat_file['hashcontent'])
        exp = QgsExpression(exp_str)

        exp.prepare(exp_context)
        if exp.hasEvalError():
            raise QgsProcessingException(
                self.tr('* ERROR: Expression %s has eval error: %s') % (exp.expression(), exp.evalErrorString()))

        request = QgsFeatureRequest(exp, exp_context)
        request.setLimit(1)

        for t in t_file.getFeatures(request):
            raise QgsProcessingException(
                self.tr('* ERREUR: le fichier %s a deja ete lu') % path)

        exp_str = QgsExpression.createFieldEqualityExpression('hashcontent', feat_file['hashcontent'])
        exp = QgsExpression(exp_str)

        exp.prepare(exp_context)
        if exp.hasEvalError():
            raise QgsProcessingException(
                self.tr('* ERROR: Expression %s has eval error: %s') % (exp.expression(), exp.evalErrorString()))

        request = QgsFeatureRequest(exp, exp_context)
        request.setLimit(1)

        for t in t_file.getFeatures(request):
            raise QgsProcessingException(
                self.tr('* ERREUR: le fichier %s semble deja avoir ete lu') % path)

        exp_context = QgsExpressionContext()
        exp_context.appendScope(QgsExpressionContextUtils.globalScope())
        exp_context.appendScope(QgsExpressionContextUtils.projectScope(context.project()))
        exp_context.appendScope(QgsExpressionContextUtils.layerScope(t_troncon))

        exp_str = 'maximum("id")'
        exp = QgsExpression(exp_str)

        exp.prepare(exp_context)
        if exp.hasEvalError():
            raise QgsProcessingException(
                self.tr('* ERROR: Expression %s has eval error: %s') % (exp.expression(), exp.evalErrorString()))

        last_t_id = exp.evaluate(exp_context)
        if not last_t_id:
            last_t_id = 0

        exp_context = QgsExpressionContext()
        exp_context.appendScope(QgsExpressionContextUtils.globalScope())
        exp_context.appendScope(QgsExpressionContextUtils.projectScope(context.project()))
        exp_context.appendScope(QgsExpressionContextUtils.layerScope(t_regard))

        exp_str = 'maximum("id")'
        exp = QgsExpression(exp_str)

        exp.prepare(exp_context)
        if exp.hasEvalError():
            raise QgsProcessingException(
                self.tr('* ERROR: Expression %s has eval error: %s') % (exp.expression(), exp.evalErrorString()))

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
                    print('Error while reading {}'.format(path))
                    raise
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

        # Dialect CSV pour la lecture des tableaux de valeurs du fichier d'ITV
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
            d = itvDialect()
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
                        b = io.StringIO(line[5:])
                        for r in csv.reader(b, d):
                            header = r
                            break
                        array = line[1:4]
                        continue
                    # Entête d'observation
                    elif line.startswith('#C'):
                        if header[0].startswith('A'):
                            obs_for_troncon = True
                        else:
                            obs_for_troncon = False
                        b = io.StringIO(line[3:])
                        for r in csv.reader(b, d):
                            header = r
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
                    b = io.StringIO(line)
                    for r in csv.reader(b, d):
                        data = r
                        row = list(zip([h.lower() for h in header], [t for t in data]))
                        # observation
                        if array == 'C':
                            if obs_for_troncon:
                                observations.append(row + [('id_troncon', t_id)])
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
        for r in regards:
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                return {self.SUCCESS: 0}

            d = dict(r)
            if d['caa'] and d['caa'] not in regard_node_refs:
                regard_node_refs.append(d['caa'])
                regard_ref_id[d['caa']] = d['id']
            if d['id'] and d['id'] > max_r_id:
                max_r_id = d['id']
            if 'cbf' in d and d['cbf'] not in itv_dates:
                itv_dates.append(d['cbf'])

        node_refs = []
        for tr in troncons:
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                return {self.SUCCESS: 0}

            d = dict(tr)
            if d['aad'] and \
                    d['aad'] not in regard_node_refs and \
                    d['aad'] not in node_refs:
                node_refs.append(d['aad'])
            if d['aaf'] and \
                    d['aaf'] not in regard_node_refs and \
                    d['aaf'] not in node_refs:
                node_refs.append(d['aaf'])
            if 'aat' in d and \
                    d['aat'] and \
                    d['aat'] not in regard_node_refs and \
                    d['aat'] not in node_refs:
                node_refs.append(d['aat'])
            if 'abf' in d and d['abf'] not in itv_dates:
                itv_dates.append(d['abf'])

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
        for tr in troncons:
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                return {self.SUCCESS: 0}

            d = dict(tr)
            if d['aad'] and \
                    d['aad'] in regard_refs:
                tr += [('id_regard1', regard_ref_id[d['aad']])]
            if d['aaf'] and \
                    d['aaf'] in regard_refs:
                tr += [('id_regard2', regard_ref_id[d['aaf']])]
            if 'aat' in d.keys() and \
                    d['aat'] and \
                    d['aat'] in regard_refs:
                tr += [('id_regard3', regard_ref_id[d['aat']])]

        # Verification des champs
        fields = provider_fields(t_troncon.fields())
        for r in troncons:
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                return {self.SUCCESS: 0}

            for k, v in r:
                # Stop the algorithm if cancel button has been clicked
                if feedback.isCanceled():
                    return {self.SUCCESS: 0}

                if fields.indexOf(k) == -1:
                    raise QgsProcessingException(
                        self.tr('* ERREUR dans le fichier : le champs de tronçon "%s" est inconnue') % k)
                field = fields.field(k)
                if isinstance(v, str) and field.isNumeric():
                    if v:
                        try:
                            float(v.replace(DECIMAL, '.'))
                        except:
                            raise QgsProcessingException(
                                self.tr('* ERREUR dans le fichier : le champs de tronçon "%s" est numérique mais pas la valeur "%s"') % (k, v))

        fields = provider_fields(t_obs.fields())
        for r in observations:
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                return {self.SUCCESS: 0}

            for k, v in r:
                # Stop the algorithm if cancel button has been clicked
                if feedback.isCanceled():
                    return {self.SUCCESS: 0}

                if fields.indexOf(k) == -1:
                    raise QgsProcessingException(
                        self.tr('* ERREUR dans le fichier : le champs d\'observation "%s" est inconnue') % k)
                field = fields.field(k)
                if isinstance(v, str) and field.isNumeric():
                    if v:
                        try:
                            float(v.replace(DECIMAL, '.'))
                        except:
                            raise QgsProcessingException(
                                self.tr('* ERREUR dans le fichier : le champs d\'observation "%s" est numérique mais pas la valeur "%s"') % (k, v))

        fields = provider_fields(t_regard.fields())
        for r in regards:
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                return {self.SUCCESS: 0}

            for k, v in r:
                # Stop the algorithm if cancel button has been clicked
                if feedback.isCanceled():
                    return {self.SUCCESS: 0}

                if fields.indexOf(k) == -1:
                    raise QgsProcessingException(
                        self.tr('* ERREUR dans le fichier : le champs de regard "%s" est inconnue') % k)
                field = fields.field(k)
                if isinstance(v, str) and field.isNumeric():
                    if v:
                        try:
                            float(v.replace(DECIMAL, '.'))
                        except:
                            raise QgsProcessingException(
                                self.tr('* ERREUR dans le fichier : le champs de regard "%s" est numérique mais pas la valeur "%s"') % (k, v))

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
                self.tr('* ERREUR: lors de l\'enregistrement du fichier %s') % ', '.join(t_file.dataProvider().errors()))
        if not t_file.commitChanges():
            raise QgsProcessingException(
                self.tr('* ERROR: Commit %s.') % t_file.commitErrors())

        # Mise a jour de l'identifiant de l'objet fichier
        feat_file.setAttribute('id', outFeats[0]['id'])

        # Creation des objets troncons
        features = []
        fields = provider_fields(t_troncon.fields())
        for r in troncons:
            feat_t = QgsFeature(fields)
            feat_t.setAttribute('id_file', feat_file['id'])
            for k, v in r:
                field = fields.field(k)
                if isinstance(v, str) and field.isNumeric():
                    if v:
                        feat_t.setAttribute(k, float(v.replace(DECIMAL, '.')))
                else:
                    feat_t.setAttribute(k, v)
            features.append(feat_t)

        # Ajout des objets troncons
        if features:
            t_troncon.startEditing()
            (res, outFeats) = t_troncon.dataProvider().addFeatures(features)
            if not res or not outFeats:
                raise QgsProcessingException(
                    self.tr('* ERREUR: lors de l\'enregistrement des troncon %s') % ', '.join(t_troncon.dataProvider().errors()))
            if not t_troncon.commitChanges():
                raise QgsProcessingException(
                    self.tr('* ERROR: Commit %s.') % t_troncon.commitErrors())

        # Creation des objets observations
        features = []
        fields = provider_fields(t_obs.fields())
        for r in observations:
            feat_o = QgsFeature(fields)
            feat_o.setAttribute('id_file', feat_file['id'])
            for k, v in r:
                field = fields.field(k)
                if isinstance(v, str) and field.isNumeric():
                    if v:
                        feat_o.setAttribute(k, float(v.replace(DECIMAL, '.')))
                else:
                    feat_o.setAttribute(k, v)
            features.append(feat_o)

        # Ajout des objets observations
        if features:
            t_obs.startEditing()
            (res, outFeats) = t_obs.dataProvider().addFeatures(features)
            if not res or not outFeats:
                raise QgsProcessingException(
                    self.tr('* ERREUR: lors de l\'enregistrement des observations %s') % ', '.join(t_obs.dataProvider().errors()))
            if not t_obs.commitChanges():
                raise QgsProcessingException(
                    self.tr('* ERROR: Commit %s.') % t_obs.commitErrors())

        # Creation des objets regards
        features = []
        fields = provider_fields(t_regard.fields())
        for r in regards:
            feat_r = QgsFeature(fields)
            feat_r.setAttribute('id_file', feat_file['id'])
            for k, v in r:
                field = fields.field(k)
                if isinstance(v, str) and field.isNumeric():
                    if v:
                        feat_r.setAttribute(k, float(v.replace(DECIMAL, '.')))
                else:
                    feat_r.setAttribute(k, v)
            features.append(feat_r)

        # Ajout des objets regards
        if features:
            t_regard.startEditing()
            (res, outFeats) = t_regard.dataProvider().addFeatures(features)
            if not res or not outFeats:
                raise QgsProcessingException(
                    self.tr('* ERREUR: lors de l\'enregistrement des regards %s') % ', '.join(t_regard.dataProvider().errors()))
            if not t_regard.commitChanges():
                raise QgsProcessingException(
                    self.tr('* ERROR: Commit %s.') % t_regard.commitErrors())

        # Returns empty dict if no outputs
        return {self.SUCCESS: 1}

    def shortHelpString(self) -> str:
        return self.tr('It will import Drain Sewer Visual Inspection data into the geopackage.')

    def name(self):
        return 'import_dsvi_data'

    def displayName(self):
        return self.tr('00 Import DSVI data')

    def group(self):
        return self.tr('Drain Sewer Visual Inspection data')

    def groupId(self):
        return 'dsvi'

    @staticmethod
    def tr(string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return self.__class__()
