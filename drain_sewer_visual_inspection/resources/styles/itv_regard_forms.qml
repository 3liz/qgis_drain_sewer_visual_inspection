<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="Forms" version="3.4.8-Madeira">
  <editform tolerant="1">/home/dhont/3Liz_ent/Clients/cabinet-merlin_marseille/08-Affaires/envoi 12-04-2019</editform>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath>/home/dhont/3Liz_ent/Clients/cabinet-merlin_marseille/08-Affaires/envoi 12-04-2019</editforminitfilepath>
  <editforminitcode><![CDATA[# -*- coding: utf-8 -*-
"""
Les formulaires QGIS peuvent avoir une fonction Python qui sera appelée à l'ouverture du formulaire.

Utilisez cette fonction pour ajouter plus de fonctionnalités à vos formulaires.

Entrez le nom de la fonction dans le champ "Fonction d'initialisation Python".
Voici un exemple à suivre:
"""
from qgis.PyQt.QtWidgets import QWidget

def my_form_open(dialog, layer, feature):
    geom = feature.geometry()
    control = dialog.findChild(QWidget, "MyLineEdit")

]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>tablayout</editorlayout>
  <attributeEditorForm>
    <attributeEditorContainer visibilityExpression="" name="Générale" visibilityExpressionEnabled="0" columnCount="1" groupBox="0" showLabel="1">
      <attributeEditorField name="id" showLabel="1" index="0"/>
      <attributeEditorField name="id_file" showLabel="1" index="53"/>
      <attributeEditorField name="caa" showLabel="1" index="1"/>
      <attributeEditorField name="id_geom_regard" showLabel="1" index="52"/>
      <attributeEditorField name="cab" showLabel="1" index="2"/>
      <attributeEditorField name="caj" showLabel="1" index="3"/>
      <attributeEditorField name="cal" showLabel="1" index="4"/>
      <attributeEditorField name="cam" showLabel="1" index="5"/>
      <attributeEditorField name="can" showLabel="1" index="6"/>
      <attributeEditorField name="cao" showLabel="1" index="7"/>
      <attributeEditorField name="cap" showLabel="1" index="8"/>
      <attributeEditorField name="caq" showLabel="1" index="9"/>
      <attributeEditorField name="car" showLabel="1" index="10"/>
      <attributeEditorField name="cas" showLabel="1" index="11"/>
    </attributeEditorContainer>
    <attributeEditorContainer visibilityExpression="" name="Détails" visibilityExpressionEnabled="0" columnCount="1" groupBox="0" showLabel="1">
      <attributeEditorField name="cba" showLabel="1" index="12"/>
      <attributeEditorField name="cbb" showLabel="1" index="13"/>
      <attributeEditorField name="cbc" showLabel="1" index="14"/>
      <attributeEditorField name="cbd" showLabel="1" index="15"/>
      <attributeEditorField name="cbe" showLabel="1" index="16"/>
      <attributeEditorField name="cbf" showLabel="1" index="17"/>
      <attributeEditorField name="cbg" showLabel="1" index="18"/>
      <attributeEditorField name="cbh" showLabel="1" index="19"/>
      <attributeEditorField name="cbi" showLabel="1" index="20"/>
      <attributeEditorField name="cbj" showLabel="1" index="21"/>
      <attributeEditorField name="cbk" showLabel="1" index="22"/>
      <attributeEditorField name="cbl" showLabel="1" index="23"/>
      <attributeEditorField name="cbm" showLabel="1" index="24"/>
      <attributeEditorField name="cbn" showLabel="1" index="25"/>
      <attributeEditorField name="cbo" showLabel="1" index="26"/>
      <attributeEditorField name="cca" showLabel="1" index="27"/>
      <attributeEditorField name="ccb" showLabel="1" index="28"/>
      <attributeEditorField name="ccc" showLabel="1" index="29"/>
      <attributeEditorField name="ccd" showLabel="1" index="30"/>
      <attributeEditorField name="ccg" showLabel="1" index="31"/>
      <attributeEditorField name="cck" showLabel="1" index="32"/>
      <attributeEditorField name="ccl" showLabel="1" index="33"/>
      <attributeEditorField name="ccm" showLabel="1" index="34"/>
      <attributeEditorField name="ccn" showLabel="1" index="35"/>
      <attributeEditorField name="cco" showLabel="1" index="36"/>
      <attributeEditorField name="ccp" showLabel="1" index="37"/>
      <attributeEditorField name="ccq" showLabel="1" index="38"/>
      <attributeEditorField name="ccr" showLabel="1" index="39"/>
      <attributeEditorField name="ccs" showLabel="1" index="40"/>
      <attributeEditorField name="cda" showLabel="1" index="41"/>
      <attributeEditorField name="cdb" showLabel="1" index="42"/>
      <attributeEditorField name="cdc" showLabel="1" index="43"/>
      <attributeEditorField name="cdd" showLabel="1" index="44"/>
      <attributeEditorField name="cde" showLabel="1" index="45"/>
      <attributeEditorField name="cea" showLabel="1" index="46"/>
      <attributeEditorField name="ceb" showLabel="1" index="47"/>
      <attributeEditorField name="ced" showLabel="1" index="48"/>
      <attributeEditorField name="cef" showLabel="1" index="49"/>
      <attributeEditorField name="ceg" showLabel="1" index="50"/>
      <attributeEditorField name="ceh" showLabel="1" index="51"/>
    </attributeEditorContainer>
  </attributeEditorForm>
  <editable>
    <field name="caa" editable="1"/>
    <field name="cab" editable="1"/>
    <field name="caj" editable="1"/>
    <field name="cal" editable="1"/>
    <field name="cam" editable="1"/>
    <field name="can" editable="1"/>
    <field name="cao" editable="1"/>
    <field name="cap" editable="1"/>
    <field name="caq" editable="1"/>
    <field name="car" editable="1"/>
    <field name="cas" editable="1"/>
    <field name="cba" editable="1"/>
    <field name="cbb" editable="1"/>
    <field name="cbc" editable="1"/>
    <field name="cbd" editable="1"/>
    <field name="cbe" editable="1"/>
    <field name="cbf" editable="1"/>
    <field name="cbg" editable="1"/>
    <field name="cbh" editable="1"/>
    <field name="cbi" editable="1"/>
    <field name="cbj" editable="1"/>
    <field name="cbk" editable="1"/>
    <field name="cbl" editable="1"/>
    <field name="cbm" editable="1"/>
    <field name="cbn" editable="1"/>
    <field name="cbo" editable="1"/>
    <field name="cca" editable="1"/>
    <field name="ccb" editable="1"/>
    <field name="ccc" editable="1"/>
    <field name="ccd" editable="1"/>
    <field name="ccg" editable="1"/>
    <field name="cck" editable="1"/>
    <field name="ccl" editable="1"/>
    <field name="ccm" editable="1"/>
    <field name="ccn" editable="1"/>
    <field name="cco" editable="1"/>
    <field name="ccp" editable="1"/>
    <field name="ccq" editable="1"/>
    <field name="ccr" editable="1"/>
    <field name="ccs" editable="1"/>
    <field name="cda" editable="1"/>
    <field name="cdb" editable="1"/>
    <field name="cdc" editable="1"/>
    <field name="cdd" editable="1"/>
    <field name="cde" editable="1"/>
    <field name="cea" editable="1"/>
    <field name="ceb" editable="1"/>
    <field name="ced" editable="1"/>
    <field name="cef" editable="1"/>
    <field name="ceg" editable="1"/>
    <field name="ceh" editable="1"/>
    <field name="id" editable="1"/>
    <field name="id_file" editable="1"/>
    <field name="id_geom_regard" editable="1"/>
  </editable>
  <labelOnTop>
    <field name="caa" labelOnTop="0"/>
    <field name="cab" labelOnTop="0"/>
    <field name="caj" labelOnTop="0"/>
    <field name="cal" labelOnTop="0"/>
    <field name="cam" labelOnTop="0"/>
    <field name="can" labelOnTop="0"/>
    <field name="cao" labelOnTop="0"/>
    <field name="cap" labelOnTop="0"/>
    <field name="caq" labelOnTop="0"/>
    <field name="car" labelOnTop="0"/>
    <field name="cas" labelOnTop="0"/>
    <field name="cba" labelOnTop="0"/>
    <field name="cbb" labelOnTop="0"/>
    <field name="cbc" labelOnTop="0"/>
    <field name="cbd" labelOnTop="0"/>
    <field name="cbe" labelOnTop="0"/>
    <field name="cbf" labelOnTop="0"/>
    <field name="cbg" labelOnTop="0"/>
    <field name="cbh" labelOnTop="0"/>
    <field name="cbi" labelOnTop="0"/>
    <field name="cbj" labelOnTop="0"/>
    <field name="cbk" labelOnTop="0"/>
    <field name="cbl" labelOnTop="0"/>
    <field name="cbm" labelOnTop="0"/>
    <field name="cbn" labelOnTop="0"/>
    <field name="cbo" labelOnTop="0"/>
    <field name="cca" labelOnTop="0"/>
    <field name="ccb" labelOnTop="0"/>
    <field name="ccc" labelOnTop="0"/>
    <field name="ccd" labelOnTop="0"/>
    <field name="ccg" labelOnTop="0"/>
    <field name="cck" labelOnTop="0"/>
    <field name="ccl" labelOnTop="0"/>
    <field name="ccm" labelOnTop="0"/>
    <field name="ccn" labelOnTop="0"/>
    <field name="cco" labelOnTop="0"/>
    <field name="ccp" labelOnTop="0"/>
    <field name="ccq" labelOnTop="0"/>
    <field name="ccr" labelOnTop="0"/>
    <field name="ccs" labelOnTop="0"/>
    <field name="cda" labelOnTop="0"/>
    <field name="cdb" labelOnTop="0"/>
    <field name="cdc" labelOnTop="0"/>
    <field name="cdd" labelOnTop="0"/>
    <field name="cde" labelOnTop="0"/>
    <field name="cea" labelOnTop="0"/>
    <field name="ceb" labelOnTop="0"/>
    <field name="ced" labelOnTop="0"/>
    <field name="cef" labelOnTop="0"/>
    <field name="ceg" labelOnTop="0"/>
    <field name="ceh" labelOnTop="0"/>
    <field name="id" labelOnTop="0"/>
    <field name="id_file" labelOnTop="0"/>
    <field name="id_geom_regard" labelOnTop="0"/>
  </labelOnTop>
  <widgets>
    <widget name="orig_ogc_fid">
      <config/>
    </widget>
  </widgets>
  <layerGeometryType>4</layerGeometryType>
</qgis>
