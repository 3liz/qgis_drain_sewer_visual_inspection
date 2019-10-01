<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="Fields" version="3.4.8-Madeira">
  <fieldConfiguration>
    <field name="id">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="false" type="bool" name="IsMultiline"/>
            <Option value="false" type="bool" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="caa">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="false" type="bool" name="IsMultiline"/>
            <Option value="false" type="bool" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="id_geom_regard">
      <editWidget type="RelationReference">
        <config>
          <Option type="Map">
            <Option value="false" type="bool" name="AllowAddFeatures"/>
            <Option value="false" type="bool" name="AllowNULL"/>
            <Option value="true" type="bool" name="MapIdentification"/>
            <Option value="false" type="bool" name="OrderByValue"/>
            <Option value="true" type="bool" name="ReadOnly"/>
            <Option type="invalid" name="Relation"/>
            <Option value="false" type="bool" name="ShowForm"/>
            <Option value="true" type="bool" name="ShowOpenFormButton"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="id_file">
      <editWidget type="RelationReference">
        <config>
          <Option type="Map">
            <Option value="false" type="bool" name="AllowAddFeatures"/>
            <Option value="false" type="bool" name="AllowNULL"/>
            <Option value="false" type="bool" name="MapIdentification"/>
            <Option value="false" type="bool" name="OrderByValue"/>
            <Option value="true" type="bool" name="ReadOnly"/>
            <Option type="invalid" name="Relation"/>
            <Option value="false" type="bool" name="ShowForm"/>
            <Option value="true" type="bool" name="ShowOpenFormButton"/>
          </Option>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias field="id" name="Identifiant" index="0"/>
    <alias field="caa" name="Ref_noeud" index="1"/>
    <alias field="id_geom_regard" name="ID_GeomRegard" index="2"/>
    <alias field="id_file" name="ID_fichierITV" index="3"/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default applyOnUpdate="0" field="id" expression=""/>
    <default applyOnUpdate="0" field="caa" expression=""/>
    <default applyOnUpdate="0" field="id_geom_regard" expression=""/>
    <default applyOnUpdate="0" field="id_file" expression=""/>
  </defaults>
  <constraints>
    <constraint constraints="3" unique_strength="1" field="id" notnull_strength="1" exp_strength="0"/>
    <constraint constraints="0" unique_strength="0" field="caa" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" unique_strength="0" field="id_geom_regard" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" unique_strength="0" field="id_file" notnull_strength="0" exp_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" desc="" field="id"/>
    <constraint exp="" desc="" field="caa"/>
    <constraint exp="" desc="" field="id_geom_regard"/>
    <constraint exp="" desc="" field="id_file"/>
  </constraintExpressions>
  <expressionfields/>
  <layerGeometryType>0</layerGeometryType>
</qgis>
