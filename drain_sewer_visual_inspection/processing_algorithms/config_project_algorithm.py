"""Config project algorithm."""

from qgis.core import (
    QgsExpression,
    QgsMapLayer,
    QgsMarkerSymbol,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterVectorLayer,
    QgsRelation,
    QgsRuleBasedRenderer,
    QgsSimpleMarkerSymbolLayer,
    QgsSimpleMarkerSymbolLayerBase,
    QgsSvgMarkerSymbolLayer,
    QgsVectorLayerJoinInfo,
)
from qgis.PyQt.QtGui import QColor

from ..qgis_plugin_tools.tools.i18n import tr
from ..qgis_plugin_tools.tools.resources import resources_path

__copyright__ = 'Copyright 2019, 3Liz'
__license__ = 'GPL version 3'
__email__ = 'info@3liz.org'
__revision__ = '$Format:%H$'


class ConfigProjectAlgorithm(QgsProcessingAlgorithm):
    FILE_TABLE = 'FILE_TABLE'
    SEGMENTS_TABLE = 'SEGMENTS_TABLE'
    OBSERVATIONS_TABLE = 'OBSERVATIONS_TABLE'
    MANHOLES_TABLE = 'MANHOLES_TABLE'

    GEOM_MANHOLES = 'GEOM_MANHOLES'
    GEOM_SEGMENT = 'GEOM_SEGMENT'
    GEOM_OBSERVATION = 'GEOM_OBSERVATION'

    VIEW_MANHOLES_GEOLOCALIZED = 'VIEW_MANHOLES_GEOLOCALIZED'

    def initAlgorithm(self, config):

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
                self.SEGMENTS_TABLE,
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

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.GEOM_MANHOLES,
                tr('Couche des géométries de regards'),
                [QgsProcessing.TypeVectorPoint],
                defaultValue='geom_regard'
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.GEOM_SEGMENT,
                tr('Couche des géométries de tronçons'),
                [QgsProcessing.TypeVectorLine],
                defaultValue='geom_troncon'
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.GEOM_OBSERVATION,
                tr('Couche des géométries d\'observations'),
                [QgsProcessing.TypeVectorPoint],
                defaultValue='geom_obs'
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.VIEW_MANHOLES_GEOLOCALIZED,
                tr('Couche des regards géolocalisés'),
                [QgsProcessing.TypeVectorPoint],
                defaultValue='view_regard_geolocalized'
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        t_file = self.parameterAsVectorLayer(
            parameters,
            self.FILE_TABLE,
            context
        )
        t_troncon = self.parameterAsVectorLayer(
            parameters,
            self.SEGMENTS_TABLE,
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

        g_regard = self.parameterAsVectorLayer(
            parameters,
            self.GEOM_MANHOLES,
            context
        )
        g_troncon = self.parameterAsVectorLayer(
            parameters,
            self.GEOM_SEGMENT,
            context
        )
        g_obs = self.parameterAsVectorLayer(
            parameters,
            self.GEOM_OBSERVATION,
            context
        )

        v_regard = self.parameterAsVectorLayer(
            parameters,
            self.VIEW_MANHOLES_GEOLOCALIZED,
            context
        )

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
        relations = [
            {
                'id': 'fk_obs_id_file',
                'name': tr('Link File - Observation'),
                'referencingLayer': t_obs.id(),
                'referencingField': 'id_file',
                'referencedLayer': t_file.id(),
                'referencedField': 'id'
            }, {
                'id': 'fk_regard_id_file',
                'name': tr('Link File - Manhole'),
                'referencingLayer': t_regard.id(),
                'referencingField': 'id_file',
                'referencedLayer': t_file.id(),
                'referencedField': 'id'
            }, {
                'id': 'fk_troncon_id_file',
                'name': tr('Link File - Pipe segment'),
                'referencingLayer': t_troncon.id(),
                'referencingField': 'id_file',
                'referencedLayer': t_file.id(),
                'referencedField': 'id'
            }, {
                'id': 'fk_obs_id_troncon',
                'name': tr('Link Pipe segment - Observation'),
                'referencingLayer': t_obs.id(),
                'referencingField': 'id_troncon',
                'referencedLayer': t_troncon.id(),
                'referencedField': 'id'
            }, {
                'id': 'fk_regard_id_geom_regard',
                'name': tr('Link Manhole inspection - Reference'),
                'referencingLayer': t_regard.id(),
                'referencingField': 'id_geom_regard',
                'referencedLayer': g_regard.id(),
                'referencedField': 'id'
            }, {
                'id': 'fk_troncon_id_geom_trononc',
                'name': tr('Link Pipe segment inspection - Reference'),
                'referencingLayer': t_troncon.id(),
                'referencingField': 'id_geom_troncon',
                'referencedLayer': g_troncon.id(),
                'referencedField': 'id'
            }
        ]

        relation_manager = context.project().relationManager()
        for rel_def in relations:
            feedback.pushInfo(
                'Link: {}'.format(rel_def['name'])
            )
            rel = QgsRelation()
            rel.setId(rel_def['id'])
            rel.setName(rel_def['name'])
            rel.setReferencingLayer(rel_def['referencingLayer'])
            rel.setReferencedLayer(rel_def['referencedLayer'])
            rel.addFieldPair(
                rel_def['referencingField'],
                rel_def['referencedField']
            )
            rel.setStrength(QgsRelation.Association)
            relation_manager.addRelation(rel)
            feedback.pushInfo(
                'Count relations {}'.format(
                    len(relation_manager.relations())
                )
            )

        joins = [
            {
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
            }
        ]
        for j_def in joins:
            layer = j_def['layer']

            join = QgsVectorLayerJoinInfo()
            join.setJoinFieldName(j_def['joinField'])
            join.setJoinLayerId(j_def['joinLayer'].id())
            join.setTargetFieldName(j_def['targetField'])

            if j_def['fieldNamesSubset']:
                join.setJoinFieldNamesSubset(j_def['fieldNamesSubset'])

            join.setUsingMemoryCache(False)
            join.setPrefix('')
            join.setEditable(False)
            join.setCascadedDelete(False)

            join.setJoinLayer(j_def['joinLayer'])

            layer.addJoin(join)
            layer.updateFields()

        # load styles
        styles = [
            {
                'layer': t_file,
                'namedStyles': [
                    {
                        'file': 'itv_file_fields.qml',
                        'type': QgsMapLayer.Fields
                    }, {
                        'file': 'itv_file_actions.qml',
                        'type': QgsMapLayer.Actions
                    }
                ]
            }, {
                'layer': t_troncon,
                'namedStyles': [
                    {
                        'file': 'itv_troncon_fields.qml',
                        'type': QgsMapLayer.Fields
                    }, {
                        'file': 'itv_troncon_table.qml',
                        'type': QgsMapLayer.AttributeTable
                    }
                ]
            }, {
                'layer': t_obs,
                'namedStyles': [
                    {
                        'file': 'itv_obs_fields.qml',
                        'type': QgsMapLayer.Fields
                    }, {
                        'file': 'itv_obs_table.qml',
                        'type': QgsMapLayer.AttributeTable
                    }
                ]
            }, {
                'layer': t_regard,
                'namedStyles': [
                    {
                        'file': 'itv_regard_fields.qml',
                        'type': QgsMapLayer.Fields
                    }, {
                        'file': 'itv_regard_forms.qml',
                        'type': QgsMapLayer.Forms
                    }, {
                        'file': 'itv_regard_table.qml',
                        'type': QgsMapLayer.AttributeTable
                    }
                ]
            }, {
                'layer': g_regard,
                'namedStyles': [
                    {
                        'file': 'itv_geom_regard_fields.qml',
                        'type': QgsMapLayer.Fields
                    }, {
                        'file': 'itv_geom_regard_symbology.qml',
                        'type': QgsMapLayer.Symbology
                    }
                ]
            }, {
                'layer': g_troncon,
                'namedStyles': [
                    {
                        'file': 'itv_geom_troncon_fields.qml',
                        'type': QgsMapLayer.Fields
                    }, {
                        'file': 'itv_geom_troncon_symbology.qml',
                        'type': QgsMapLayer.Symbology
                    }, {
                        'file': 'itv_geom_troncon_actions.qml',
                        'type': QgsMapLayer.Actions
                    }
                ]
            }, {
                'layer': g_obs,
                'namedStyles': [
                    {
                        'file': 'itv_geom_obs_fields.qml',
                        'type': QgsMapLayer.Fields
                    }, {
                        'file': 'itv_geom_obs_symbology.qml',
                        'type': QgsMapLayer.Symbology
                    }
                ]
            }, {
                'layer': v_regard,
                'namedStyles': [
                    {
                        'file': 'itv_view_regard_fields.qml',
                        'type': QgsMapLayer.Fields
                    }, {
                        'file': 'itv_view_regard_symbology.qml',
                        'type': QgsMapLayer.Symbology
                    }, {
                        'file': 'itv_view_regard_labeling.qml',
                        'type': QgsMapLayer.Labeling
                    }
                ]
            }
        ]
        for style in styles:
            layer = style['layer']
            for n_style in style['namedStyles']:
                layer.loadNamedStyle(
                    resources_path('styles', n_style['file']),
                    categories=n_style['type']
                )
                # layer.saveStyleToDatabase('style', 'default style', True, '')
                layer.triggerRepaint()

        # Creation de la symbologie g_obs
        g_obs_rules = (
            'BAA', 'BAB', 'BAC', 'BAD', 'BAE', 'BAF', 'BAG', 'BAH',
            'BAI', 'BAJ', 'BAK', 'BAL', 'BAM', 'BAN', 'BAO', 'BAP',
            'BBA', 'BBB', 'BBC', 'BBD', 'BBE', 'BBF', 'BBG', 'BBH',
            'BCA', 'BCB', 'BCC', 'BDA', 'BDB', 'BDC', 'BDD', 'BDE',
            'BDF', 'BDG'
        )
        g_obs_rule_descs = {
            'BAA': 'Déformation',
            'BAB': 'Fissure',
            'BAC': 'Rupture/Effondrement',
            'BAD': 'Elt maçonnerie',
            'BAE': 'Mortier manquant',
            'BAF': 'Dégradation de surface',
            'BAG': 'Branchement pénétrant',
            'BAH': 'Raccordement défectueux',
            'BAI': 'Joint étanchéité apparent',
            'BAJ': 'Déplacement d\'assemblage',
            'BAK': 'Défaut de révêtement',
            'BAL': 'Réparation défectueuse',
            'BAM': 'Défaut soudure',
            'BAN': 'Conduite poreuse',
            'BAO': 'Sol visible',
            'BAP': 'Trou visible',
            'BBA': 'Racines',
            'BBB': 'Dépots Adhérents',
            'BBC': 'Dépôts',
            'BBD': 'Entrée de terre',
            'BBE': 'Autres obstacles',
            'BBF': 'Infiltration',
            'BBG': 'Exfiltration',
            'BBH': 'Vermine',
            'BCA': 'Raccordement',
            'BCB': 'Réparation',
            'BCC': 'Courbure de collecteur',
            'BDA': 'Photographie générale',
            'BDB': 'Remarque générale',
            'BDC': 'Inspection abandonnée',
            'BDD': 'Niveau d\'eau',
            'BDE': 'Ecoulement dans une canlisation entrante',
            'BDF': 'Atmosphère canalisation',
            'BDG': 'Perte de visibilité'
        }
        g_obs_rootrule = QgsRuleBasedRenderer.Rule(None)
        rendering_pass_idx = len(g_obs_rules)
        for rule in g_obs_rules:
            # get svg path
            svg_path = resources_path('styles', 'img_obs', rule + '.svg')
            # create svg symbol layer
            svg_symbol_layer = QgsSvgMarkerSymbolLayer(svg_path)
            svg_symbol_layer.setRenderingPass(rendering_pass_idx)
            # create white square symbol layer for the backend
            simple_symbol_layer = QgsSimpleMarkerSymbolLayer(
                shape=QgsSimpleMarkerSymbolLayerBase.Circle,
                size=svg_symbol_layer.size(),
                color=QColor('white'),
                strokeColor=QColor('white')
            )
            simple_symbol_layer.setRenderingPass(rendering_pass_idx)
            # create marker
            svg_marker = QgsMarkerSymbol()
            # set the backend symbol layer
            svg_marker.changeSymbolLayer(0, simple_symbol_layer)
            # add svg symbol layer
            svg_marker.appendSymbolLayer(svg_symbol_layer)
            # create rule
            svg_rule = QgsRuleBasedRenderer.Rule(
                svg_marker, 0, 10000,
                QgsExpression.createFieldEqualityExpression('a', rule),
                rule
            )
            if rule in g_obs_rule_descs:
                svg_rule.setLabel(g_obs_rule_descs[rule])
                svg_rule.setDescription('{}: {}'.format(
                    rule,
                    g_obs_rule_descs[rule]
                ))
            # add rule
            g_obs_rootrule.appendChild(svg_rule)
            rendering_pass_idx -= 1
        g_obs_rootrule.appendChild(
            QgsRuleBasedRenderer.Rule(
                QgsMarkerSymbol.createSimple(
                    {
                        'name': 'circle',
                        'color': '#0000b2',
                        'outline_color': '#0000b2',
                        'size': '1'
                    }
                ),
                0, 10000, 'ELSE', 'Autres'
            )
        )
        g_obs.setRenderer(QgsRuleBasedRenderer(g_obs_rootrule))
        feedback.pushInfo('Project has been setup')
        return {}

    def shortHelpString(self) -> str:
        return tr('Create project variables according to layers.')

    def name(self):
        return 'config_dsvi_project'

    def displayName(self):
        return '{} {}'.format('05', tr('Project configuration'))

    def group(self):
        return tr('Configuration')

    def groupId(self):
        return 'configuration'

    def createInstance(self):
        return self.__class__()
