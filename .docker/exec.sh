#!/usr/bin/env bash

docker exec -it qgis sh -c "cd /tests_directory/drain_sewer_visual_inspection && qgis_testrunner.sh qgis_plugin_tools.infrastructure.test_runner.test_package"
