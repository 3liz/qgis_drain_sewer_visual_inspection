LOCALES = fr
PLUGINNAME = drain_sewer_visual_inspection

i18n_%:
	$(MAKE) -C qgis_plugin_tools $* LOCALES=$(LOCALES)

deploy_%:
	$(MAKE) -C qgis_plugin_tools $* PLUGINNAME=$(PLUGINNAME)