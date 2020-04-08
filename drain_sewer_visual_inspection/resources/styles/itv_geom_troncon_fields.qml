<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="Fields" version="3.4.8-Madeira">
  <fieldConfiguration>
    <field name="id">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" value="0" name="IsMultiline"/>
            <Option type="QString" value="0" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="label">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="id_geom_regard_amont">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="bool" value="false" name="IsMultiline"/>
            <Option type="bool" value="false" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="id_geom_regard_aval">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option type="QString" value="0" name="IsMultiline"/>
            <Option type="QString" value="0" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias field="id" index="0" name="Identifiant"/>
    <alias field="label" index="1" name="Référence"/>
    <alias field="id_geom_regard_amont" index="2" name="Identifiant de la géométrie de regard amont"/>
    <alias field="id_geom_regard_aval" index="3" name="Identifiant de la géométrie de regard aval"/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default applyOnUpdate="0" field="id" expression=""/>
    <default applyOnUpdate="0" field="label" expression=""/>
    <default applyOnUpdate="0" field="id_geom_regard_amont" expression=""/>
    <default applyOnUpdate="0" field="id_geom_regard_aval" expression=""/>
  </defaults>
  <constraints>
    <constraint constraints="3" unique_strength="1" field="id" notnull_strength="1" exp_strength="0"/>
    <constraint constraints="0" unique_strength="0" field="label" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" unique_strength="0" field="id_geom_regard_amont" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" unique_strength="0" field="id_geom_regard_aval" notnull_strength="0" exp_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint desc="" field="id" exp=""/>
    <constraint desc="" field="label" exp=""/>
    <constraint desc="" field="id_geom_regard_amont" exp=""/>
    <constraint desc="" field="id_geom_regard_aval" exp=""/>
  </constraintExpressions>
  <expressionfields/>
  <layerGeometryType>1</layerGeometryType>
</qgis>
