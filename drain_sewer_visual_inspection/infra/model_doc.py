#!/usr/bin/env python3
import os

from os.path import join

from qgis.PyQt.QtCore import QVariant
from qgis.core import QgsVectorLayer

from drain_sewer_visual_inspection.processing_algorithms.create_data_model_algorithm import MAPPING
from drain_sewer_visual_inspection.qgis_plugin_tools.tools.resources import resources_path

# Hardcoded for now, need to reuse "create_data_model_algorithm.py" TODO
relations = [
    {
        'id': 'fk_obs_id_file',
        'name': 'Link File - Observation',
        'referencingLayer': 'obs',
        'referencingField': 'id_file',
        'referencedLayer': 'file',
        'referencedField': 'id'
    }, {
        'id': 'fk_regard_id_file',
        'name': 'Link File - Manhole',
        'referencingLayer': 'regard',
        'referencingField': 'id_file',
        'referencedLayer': 'file',
        'referencedField': 'id'
    }, {
        'id': 'fk_troncon_id_file',
        'name': 'Link File - Pipe segment',
        'referencingLayer': 'troncon',
        'referencingField': 'id_file',
        'referencedLayer': 'file',
        'referencedField': 'id'
    }, {
        'id': 'fk_obs_id_troncon',
        'name': 'Link Pipe segment - Observation',
        'referencingLayer': 'obs',
        'referencingField': 'id_troncon',
        'referencedLayer': 'troncon',
        'referencedField': 'id'
    }, {
        'id': 'fk_regard_id_geom_regard',
        'name': 'Link Manhole inspection - Reference',
        'referencingLayer': 'regard',
        'referencingField': 'id_geom_regard',
        'referencedLayer': 'geom_regard',
        'referencedField': 'id'
    }, {
        'id': 'fk_troncon_id_geom_trononc',
        'name': 'Link Pipe segment inspection - Reference',
        'referencingLayer': 'troncon',
        'referencingField': 'id_geom_troncon',
        'referencedLayer': 'geom_troncon',
        'referencedField': 'id'
    }
]

PATH = '/model'

TEMPLATE = '''---
hide:
  - navigation
---

# Modèle de données

## Relations

??? info "Légende"
    Flèche pleine : relation de projet

    Losange vide : jointure spatiale

{relationships}

## Tables

??? info "Légende"
    Champ géométrique en *italique*

    Champ de clé primaire en **gras**

    <!-- Champ de clé étrangère cliquable avec la mention "FK" -->

'''

TEMPLATE_TABLE = '''### {name}

| ID | Name | Type | Alias |
|:-:|:-:|:-:|:-:|
{fields}
'''

TEMPLATE_FIELDS = '|{id}|{name}|{type}|{alias}|\n'

TEMPLATE_MERMAID = '''\'\'\'classDiagram
\'\'\'
'''

# view_regard_geolocalized <!-- regard
# view_regard_geolocalized <!-- geom_regard
# view_regard_geolocalized : geom Point
# view_regard_geolocalized : id PK
# view_regard_geolocalized : caa
# view_regard_geolocalized : id_geom_regard
# view_regard_geolocalized : id_file

def slug(table):
    return table.replace('_', '-')


def find_relation(field_name, table):
    for relation in relations:
        relation: Relation
        if relation.referencing_layer == table and relation.referencing_field == field_name:
            return relation.referenced_layer
        elif relation.referenced_layer == table and relation.referenced_field == field_name:
            return relation.referencing_layer

def generate_model_doc():  # NOQA C901
    global TEMPLATE

    markdown_all = TEMPLATE

    files = os.listdir(resources_path('data_models'))
    mermaid_md = '```mermaid\n'
    mermaid_md += 'classDiagram\n'

    mermaid_field_md = ''

    for csv_file in files:
        if csv_file.endswith('csvt'):
            continue
        table_name = csv_file.replace('.csv', '')

        if table_name == 'metadata':
            continue

        md = ''

        # Ajout de la geom
        if MAPPING[table_name][0] is not None:
            field_md = TEMPLATE_FIELDS.format(
                id='',
                name='*geom*',
                type=MAPPING[table_name][0],
                alias='',
            )
            md += field_md
            mermaid_field_md += '{} : geom {}\n'.format(
                table_name,
                MAPPING[table_name][0],
            )

        mermaid_md += table_name + '\n'
        pretty_name = table_name.replace('_', ' ')
        pretty_name = pretty_name.title()

        csv_path = resources_path('data_models', '{}.csv'.format(table_name))
        csv = QgsVectorLayer(csv_path, table_name, 'ogr')

        for i, field in enumerate(csv.getFeatures()):

            display_name = mermaid_display_name = field['name']

            if display_name == 'id':
                display_name = '**' + display_name + '**'
                mermaid_display_name += ' PK'

            if display_name.endswith('_id'):
                display_name = '[{title} FK](#{anchor})'.format(
                    title=display_name,
                    anchor=slug(find_relation(field['name'], table_name))
                )
                mermaid_display_name += ' FK'

            field_md = TEMPLATE_FIELDS.format(
                id=field['idx'],
                name=display_name,
                type=QVariant.typeToName(int(field['type'])),
                alias=field['alias'],
            )
            md += field_md

            if i < 10:
                mermaid_field_md += '{} : {}\n'.format(
                    table_name,
                    mermaid_display_name,
                )
            elif i == 10:
                mermaid_field_md += '{} : ...\n'.format(table_name)

        markdown = TEMPLATE_TABLE.format(name=pretty_name, fields=md)
        markdown_all += markdown

    for relation in relations:
        mermaid_md += '{} <|-- {}\n'.format(
            relation['referencedLayer'],
            relation['referencingLayer'],
        )

    mermaid_md += mermaid_field_md
    mermaid_md += '```'
    markdown_all = markdown_all.format(relationships=mermaid_md)

    output_file = join(PATH, 'README.md')
    output_file = '/home/etienne/dev/python/dsvi/docs/model.md'
    text_file = open(output_file, "w+")
    text_file.write(markdown_all)
    text_file.close()


generate_model_doc()
