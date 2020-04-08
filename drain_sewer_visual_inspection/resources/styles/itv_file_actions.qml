<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="Actions" version="3.4.7-Madeira">
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
    <actionsetting id="{2c6f8525-87e9-4105-a206-e0f7da8e4c7e}" capture="0" shortTitle="Select children and Feature" icon="" isEnabledOnlyWhenEditable="0" type="1" action="from qgis.core import QgsVectorLayer&#xa;&#xa;project = QgsProject.instance()&#xa;layer = QgsProject.instance().mapLayer('[% @layer_id %]')&#xa;feat = layer.getFeature( [% $id %] )&#xa;&#xa;relations = project.relationManager().referencedRelations(layer)&#xa;for relation in relations:&#xa;    referencingLayer = relation.referencingLayer()&#xa;    relatedFeatureExpression = relation.getRelatedFeaturesFilter(feat)&#xa;    referencingLayer.selectByExpression(relatedFeatureExpression, QgsVectorLayer.AddToSelection)&#xa;&#xa;layer.selectByIds([feat.id()], QgsVectorLayer.AddToSelection)" name="Select children and Feature" notificationMessage="">
      <actionScope id="Feature"/>
    </actionsetting>
    <actionsetting id="{78db319c-ea9c-44f5-8b1d-53523a1a7a0b}" capture="0" shortTitle="Delete children and Feature" icon="" isEnabledOnlyWhenEditable="0" type="1" action="from qgis.core import QgsVectorDataProvider, edit&#xa;&#xa;project = QgsProject.instance()&#xa;layer = QgsProject.instance().mapLayer('[% @layer_id %]')&#xa;feat = layer.getFeature( [% $id %] )&#xa;&#xa;relations = project.relationManager().referencedRelations(layer)&#xa;for relation in relations:&#xa;    referencingLayer = relation.referencingLayer()&#xa;    referencingCaps = referencingLayer.dataProvider().capabilities()&#xa;    if not referencingCaps &amp; QgsVectorDataProvider.DeleteFeatures:&#xa;        continue&#xa;    &#xa;    relatedFeatureExpression = relation.getRelatedFeaturesFilter(feat)&#xa;    with edit(referencingLayer):&#xa;        referencingLayer.selectByExpression(relatedFeatureExpression)&#xa;        referencingLayer.deleteSelectedFeatures()&#xa;&#xa;caps = layer.dataProvider().capabilities()&#xa;if caps &amp; QgsVectorDataProvider.DeleteFeatures:&#xa;    with edit(layer):&#xa;        layer.selectByIds(feat.id())&#xa;        layer.deleteSelectedFeatures()" name="Delete children and Feature" notificationMessage="">
      <actionScope id="Feature"/>
    </actionsetting>
  </attributeactions>
  <layerGeometryType>4</layerGeometryType>
</qgis>
