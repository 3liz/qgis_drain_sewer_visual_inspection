<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="Actions" version="3.4.7-Madeira">
  <attributeactions>
    <defaultAction value="{1c0f8dca-e5e5-40c7-8214-54a677571f50}" key="Canvas"/>
    <actionsetting id="{990146ae-2121-40d7-89d8-c0a188393fd3}" capture="0" shortTitle="Delete and update children" icon="" isEnabledOnlyWhenEditable="0" type="1" action="from qgis.core import QgsVectorDataProvider, edit&#xa;&#xa;project = QgsProject.instance()&#xa;layer = QgsProject.instance().mapLayer('[% @layer_id %]')&#xa;feat = layer.getFeature( [% $id %] )&#xa;&#xa;relations = project.relationManager().referencedRelations(layer)&#xa;for relation in relations:&#xa;    referencingLayer = relation.referencingLayer()&#xa;    relatedFeatureExpression = relation.getRelatedFeaturesFilter(feat)&#xa;    referencingLayer.selectByExpression(relatedFeatureExpression)&#xa;    &#xa;    referencingCaps = referencingLayer.dataProvider().capabilities()&#xa;    if referencingCaps &amp; QgsVectorDataProvider.ChangeAttributeValues:&#xa;        attrs = { relation.referencingFields()[0] : None }&#xa;        with edit(referencingLayer):&#xa;            for f in referencingLayer.getSelectedFeatures():&#xa;                fid = f.id()&#xa;                referencingLayer.dataProvider().changeAttributeValues({ fid : attrs })&#xa;                &#xa;caps = layer.dataProvider().capabilities()&#xa;if caps &amp; QgsVectorDataProvider.DeleteFeatures:&#xa;    with edit(layer):&#xa;        layer.selectByIds([feat.id()])&#xa;        layer.deleteSelectedFeatures()" name="Delete and update children" notificationMessage="">
      <actionScope id="Canvas"/>
      <actionScope id="Feature"/>
    </actionsetting>
  </attributeactions>
  <layerGeometryType>1</layerGeometryType>
</qgis>
