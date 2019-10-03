"""Config project algorithm."""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QColor
from qgis.core import (
    QgsMapLayer,
    QgsVectorLayerJoinInfo,
    QgsRelation,
    QgsExpression,
    QgsRuleBasedRenderer,
    QgsSvgMarkerSymbolLayer,
    QgsSimpleMarkerSymbolLayer,
    QgsSimpleMarkerSymbolLayerBase,
    QgsMarkerSymbol)
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterVectorLayer,
    QgsProcessingOutputNumber)

from ..qgis_plugin_tools.resources import resources_path

__copyright__ = "Copyright 2019, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = '$Format:%H$'


class ConfigProjectAlgorithm(QgsProcessingAlgorithm):

    TABLE_FICHIER = 'TABLE_FICHIER'
    TABLE_TRONCON = 'TABLE_TRONCON'
    TABLE_OBSERVATIONS = 'TABLE_OBSERVATIONS'
    TABLE_REGARD = 'TABLE_REGARD'

    COUCHE_GEOM_REGARD = 'COUCHE_GEOM_REGARD'
    COUCHE_GEOM_TRONCON = 'COUCHE_GEOM_TRONCON'
    COUCHE_GEOM_OBSERVATION = 'COUCHE_GEOM_OBSERVATION'

    VIEW_REGARD_GEOLOCALIZED = 'VIEW_REGARD_GEOLOCALIZED'

    SUCCESS = 'SUCCESS'

    def initAlgorithm(self, config):

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.TABLE_FICHIER,
                self.tr('Tableau des fichiers d\'ITV importés'),
                [QgsProcessing.TypeVector],
                defaultValue='file'
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.TABLE_TRONCON,
                self.tr('Tableau des tronçons d\'ITV'),
                [QgsProcessing.TypeVector],
                defaultValue='troncon'
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.TABLE_OBSERVATIONS,
                self.tr('Tableau des observations d\'ITV'),
                [QgsProcessing.TypeVector],
                defaultValue='obs'
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.TABLE_REGARD,
                self.tr('Tableau des regards d\'ITV'),
                [QgsProcessing.TypeVector],
                defaultValue='regard'
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.COUCHE_GEOM_REGARD,
                self.tr('Couche des géométries de regards'),
                [QgsProcessing.TypeVectorPoint],
                defaultValue='geom_regard'
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.COUCHE_GEOM_TRONCON,
                self.tr('Couche des géométries de tronçons'),
                [QgsProcessing.TypeVectorLine],
                defaultValue='geom_troncon'
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.COUCHE_GEOM_OBSERVATION,
                self.tr('Couche des géométries d\'observations'),
                [QgsProcessing.TypeVectorPoint],
                defaultValue='geom_obs'
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.VIEW_REGARD_GEOLOCALIZED,
                self.tr('Couche des regards géolocalisés'),
                [QgsProcessing.TypeVectorPoint],
                defaultValue='view_regard_geolocalized'
            )
        )

        # self.addOutput(QgsProcessingOutputNumber(self.SUCCESS, self.tr('Succès')))

    def processAlgorithm(self, parameters, context, feedback):

        t_file = self.parameterAsVectorLayer(parameters, self.TABLE_FICHIER, context)
        t_troncon = self.parameterAsVectorLayer(parameters, self.TABLE_TRONCON, context)
        t_obs = self.parameterAsVectorLayer(parameters, self.TABLE_OBSERVATIONS, context)
        t_regard = self.parameterAsVectorLayer(parameters, self.TABLE_REGARD, context)

        g_regard = self.parameterAsVectorLayer(parameters, self.COUCHE_GEOM_REGARD, context)
        g_troncon = self.parameterAsVectorLayer(parameters, self.COUCHE_GEOM_TRONCON, context)
        g_obs = self.parameterAsVectorLayer(parameters, self.COUCHE_GEOM_OBSERVATION, context)

        v_regard = self.parameterAsVectorLayer(parameters, self.VIEW_REGARD_GEOLOCALIZED, context)

        # define variables
        variables = context.project().customVariables()
        variables['itv_rerau_t_file'] = t_file.id()
        variables['itv_rerau_t_troncon'] = t_troncon.id()
        variables['itv_rerau_t_obs'] = t_obs.id()
        variables['itv_rerau_t_regard'] = t_regard.id()

        variables['itv_rerau_g_regard'] = g_regard.id()
        variables['itv_rerau_g_troncon'] = g_troncon.id()
        variables['itv_rerau_g_obs'] = g_obs.id()

        context.project().setCustomVariables(variables)

        # define relations
        relations = [{
            'id': 'fk_obs_id_file',
            'name': 'Liens Fichier - Observation',
            'referencingLayer': t_obs.id(),
            'referencingField': 'id_file',
            'referencedLayer': t_file.id(),
            'referencedField': 'id'
        }, {
            'id': 'fk_regard_id_file',
            'name': 'Liens Fichier - Regard',
            'referencingLayer': t_regard.id(),
            'referencingField': 'id_file',
            'referencedLayer': t_file.id(),
            'referencedField': 'id'
        }, {
            'id': 'fk_troncon_id_file',
            'name': 'Liens Fichier - Tronçon',
            'referencingLayer': t_troncon.id(),
            'referencingField': 'id_file',
            'referencedLayer': t_file.id(),
            'referencedField': 'id'
        }, {
            'id': 'fk_obs_id_troncon',
            'name': 'Liens Tronçon - Observation',
            'referencingLayer': t_obs.id(),
            'referencingField': 'id_troncon',
            'referencedLayer': t_troncon.id(),
            'referencedField': 'id'
        }, {
            'id': 'fk_regard_id_geom_regard',
            'name': 'Liens Inspection regard - Référence',
            'referencingLayer': t_regard.id(),
            'referencingField': 'id_geom_regard',
            'referencedLayer': g_regard.id(),
            'referencedField': 'id'
        }, {
            'id': 'fk_troncon_id_geom_trononc',
            'name': 'Liens Inspection tronçon - Référence',
            'referencingLayer': t_troncon.id(),
            'referencingField': 'id_geom_troncon',
            'referencedLayer': g_troncon.id(),
            'referencedField': 'id'
        }]

        relation_manager = context.project().relationManager()
        for r in relations:
            feedback.pushInfo(r['name'])
            rel = QgsRelation()
            rel.setId(r['id'])
            rel.setName(r['name'])
            rel.setReferencingLayer(r['referencingLayer'])
            rel.setReferencedLayer(r['referencedLayer'])
            rel.addFieldPair(r['referencingField'], r['referencedField'])
            rel.setStrength(QgsRelation.Association)
            relation_manager.addRelation(rel)
            feedback.pushInfo('Count relations {}'.format(len(relation_manager.relations())))

        joins = [{
            'layer': t_obs,
            'targetField': 'id_troncon',
            'joinLayer': t_troncon,
            'joinField': 'id',
            'fieldNamesSubset': ['ack']
        }, {
            'layer': g_obs,
            'targetField': 'id',
            'joinLayer': t_obs,
            'joinField': 'id',
            'fieldNamesSubset': []
        }]
        for j in joins:
            layer = j['layer']

            join = QgsVectorLayerJoinInfo()
            join.setTargetFieldName(j['targetField'])
            join.setJoinLayer(j['joinLayer'])
            join.setJoinFieldName(j['joinField'])

            if j['fieldNamesSubset']:
                join.setJoinFieldNamesSubset(j['fieldNamesSubset'])

            join.setUsingMemoryCache(False)
            join.setPrefix('')
            join.setEditable(False)
            join.setCascadedDelete(False)

            layer.addJoin(join)
            layer.updateFields()

        # load styles
        styles = [{
            'layer': t_file,
            'namedStyles': [{
                'file': 'itv_file_fields.qml',
                'type': QgsMapLayer.Fields
            }, {
                'file': 'itv_file_actions.qml',
                'type': QgsMapLayer.Actions
            }]
        }, {
            'layer': t_troncon,
            'namedStyles': [{
                'file': 'itv_troncon_fields.qml',
                'type': QgsMapLayer.Fields
            }, {
                'file': 'itv_troncon_table.qml',
                'type': QgsMapLayer.AttributeTable
            }]
        }, {
            'layer': t_obs,
            'namedStyles': [{
                'file': 'itv_obs_fields.qml',
                'type': QgsMapLayer.Fields
            }, {
                'file': 'itv_obs_table.qml',
                'type': QgsMapLayer.AttributeTable
            }]
        }, {
            'layer': t_regard,
            'namedStyles': [{
                'file': 'itv_regard_fields.qml',
                'type': QgsMapLayer.Fields
            }, {
                'file': 'itv_regard_forms.qml',
                'type': QgsMapLayer.Forms
            }, {
                'file': 'itv_regard_table.qml',
                'type': QgsMapLayer.AttributeTable
            }]
        }, {
            'layer': g_regard,
            'namedStyles': [{
                'file': 'itv_geom_regard_fields.qml',
                'type': QgsMapLayer.Fields
            }, {
                'file': 'itv_geom_regard_symbology.qml',
                'type': QgsMapLayer.Symbology
            }]
        }, {
            'layer': g_troncon,
            'namedStyles': [{
                'file': 'itv_geom_troncon_fields.qml',
                'type': QgsMapLayer.Fields
            }, {
                'file': 'itv_geom_troncon_symbology.qml',
                'type': QgsMapLayer.Symbology
            }, {
                'file': 'itv_geom_troncon_actions.qml',
                'type': QgsMapLayer.Actions
            }]
        }, {
            'layer': g_obs,
            'namedStyles': [{
                'file': 'itv_geom_obs_fields.qml',
                'type': QgsMapLayer.Fields
            }, {
                'file': 'itv_geom_obs_symbology.qml',
                'type': QgsMapLayer.Symbology
            }]
        }, {
            'layer': v_regard,
            'namedStyles': [{
                'file': 'itv_view_regard_fields.qml',
                'type': QgsMapLayer.Fields
            }, {
                'file': 'itv_view_regard_symbology.qml',
                'type': QgsMapLayer.Symbology
            }, {
                'file': 'itv_view_regard_labeling.qml',
                'type': QgsMapLayer.Labeling
            }]
        }]
        for s in styles:
            layer = s['layer']
            for n in s['namedStyles']:
                layer.loadNamedStyle(resources_path('styles', n['file']), categories=n['type'])
                layer.triggerRepaint()

        # Creation de la symbologie g_obs
        g_obs_rules = ('BAA', 'BAB', 'BAC', 'BAD', 'BAF', 'BAG', 'BAI', 'BAJ',
                       'BBA', 'BBB', 'BBC', 'BBE', 'BBF', 'BCB', 'BDC')
        g_obs_rootrule = QgsRuleBasedRenderer.Rule(None)
        for r in g_obs_rules:
            # get svg path
            svg_path = resources_path('styles', 'img_obs', r + '.svg')
            # create svg symbol layer
            svg_symbol_layer = QgsSvgMarkerSymbolLayer(svg_path)
            # create white square symbol layer for the backend
            simple_symbol_layer = QgsSimpleMarkerSymbolLayer(
                shape=QgsSimpleMarkerSymbolLayerBase.Circle,
                size=svg_symbol_layer.size(),
                color=QColor('white'),
                strokeColor=QColor('white')
            )
            # create marker
            svg_marker = QgsMarkerSymbol()
            # set the backend symbol layer
            svg_marker.changeSymbolLayer(0, simple_symbol_layer)
            # add svg symbol layer
            svg_marker.appendSymbolLayer(svg_symbol_layer)
            # create rule
            svg_rule = QgsRuleBasedRenderer.Rule(svg_marker, 0, 10000, QgsExpression.createFieldEqualityExpression('a', r), r)
            # add rule
            g_obs_rootrule.appendChild(svg_rule)
        g_obs_rootrule.appendChild(
            QgsRuleBasedRenderer.Rule(
                QgsMarkerSymbol.createSimple({'name': 'circle', 'color': '#0000b2', 'outline_color': '#0000b2', 'size': '1'}),
                0, 10000, 'ELSE', 'Autres'
            )
        )
        g_obs.setRenderer(QgsRuleBasedRenderer(g_obs_rootrule))
        feedback.pushInfo('Project has been setup')
        return {}

    def shortHelpString(self) -> str:
        return self.tr('Create project variables according to layers.')

    def name(self):
        return 'config_dsvi_project'

    def displayName(self):
        return self.tr('05 Project configuration')

    def group(self):
        return self.tr('Configuration')

    def groupId(self):
        return 'configuration'

    @staticmethod
    def tr(string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return self.__class__()
