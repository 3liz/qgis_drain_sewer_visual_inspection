<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.4.8-Madeira" styleCategories="Fields">
  <fieldConfiguration>
    <field name="id">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="basename">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="encoding">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="lang">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="version">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="hashcontent">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="0" type="QString" name="IsMultiline"/>
            <Option value="0" type="QString" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="date_debut">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="false" type="bool" name="IsMultiline"/>
            <Option value="false" type="bool" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="date_fin">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="false" type="bool" name="IsMultiline"/>
            <Option value="false" type="bool" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias field="id" index="0" name="Id"/>
    <alias field="basename" index="1" name="Nom"/>
    <alias field="encoding" index="2" name="Encodage"/>
    <alias field="lang" index="3" name="Langue"/>
    <alias field="version" index="4" name="Version"/>
    <alias field="hashcontent" index="5" name="Hash"/>
    <alias field="date_debut" index="6" name="Date début"/>
    <alias field="date_fin" index="7" name="Date fin"/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default applyOnUpdate="0" field="id" expression=""/>
    <default applyOnUpdate="0" field="basename" expression=""/>
    <default applyOnUpdate="0" field="encoding" expression=""/>
    <default applyOnUpdate="0" field="lang" expression=""/>
    <default applyOnUpdate="0" field="version" expression=""/>
    <default applyOnUpdate="0" field="hashcontent" expression=""/>
    <default applyOnUpdate="0" field="date_debut" expression=""/>
    <default applyOnUpdate="0" field="date_fin" expression=""/>
  </defaults>
  <constraints>
    <constraint exp_strength="0" unique_strength="1" field="id" notnull_strength="1" constraints="3"/>
    <constraint exp_strength="0" unique_strength="0" field="basename" notnull_strength="0" constraints="0"/>
    <constraint exp_strength="0" unique_strength="0" field="encoding" notnull_strength="0" constraints="0"/>
    <constraint exp_strength="0" unique_strength="0" field="lang" notnull_strength="0" constraints="0"/>
    <constraint exp_strength="0" unique_strength="0" field="version" notnull_strength="0" constraints="0"/>
    <constraint exp_strength="0" unique_strength="0" field="hashcontent" notnull_strength="0" constraints="0"/>
    <constraint exp_strength="0" unique_strength="0" field="date_debut" notnull_strength="0" constraints="0"/>
    <constraint exp_strength="0" unique_strength="0" field="date_fin" notnull_strength="0" constraints="0"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" desc="" field="id"/>
    <constraint exp="" desc="" field="basename"/>
    <constraint exp="" desc="" field="encoding"/>
    <constraint exp="" desc="" field="lang"/>
    <constraint exp="" desc="" field="version"/>
    <constraint exp="" desc="" field="hashcontent"/>
    <constraint exp="" desc="" field="date_debut"/>
    <constraint exp="" desc="" field="date_fin"/>
  </constraintExpressions>
  <expressionfields/>
  <layerGeometryType>4</layerGeometryType>
</qgis>
