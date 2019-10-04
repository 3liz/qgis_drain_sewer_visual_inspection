LOCALES = fr
PLUGINNAME = drain_sewer_visual_inspection

docker_test:
	$(MAKE) -C qgis_plugin_tools docker_test PLUGINNAME=$(PLUGINNAME)

i18n_%:
	$(MAKE) -C qgis_plugin_tools $* LOCALES=$(LOCALES)

deploy_%:
	$(MAKE) -C qgis_plugin_tools $* PLUGINNAME=$(PLUGINNAME)