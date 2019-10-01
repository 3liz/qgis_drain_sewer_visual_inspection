docker run -d --name qgis-testing-environment -v ${PWD}:/qgis_drain_sewer_visual_inspection -e DISPLAY=:99 qgis/qgis:release-3_4
sleep 10
docker exec -it qgis-testing-environment sh -c "qgis_setup.sh qgis_drain_sewer_visual_inspection"
docker exec -it qgis-testing-environment sh -c "rm -f  /root/.local/share/QGIS/QGIS3/profiles/default/python/plugins/qgis_drain_sewer_visual_inspection"
docker exec -it qgis-testing-environment sh -c "ln -s /qgis_drain_sewer_visual_inspection/ /root/.local/share/QGIS/QGIS3/profiles/default/python/plugins/qgis_drain_sewer_visual_inspection"
docker exec -it qgis-testing-environment sh -c "export PYTHONPATH=${PYTHONPATH}:/"
  # - docker exec -it qgis-testing-environment sh -c "pip3 install -r /QuickOSM/requirements_dev.txt"

docker exec -it qgis-testing-environment sh -c "cd /qgis_drain_sewer_visual_inspection && qgis_testrunner.sh test_runner.test_package"

docker stop qgis-testing-environment
docker rm qgis-testing-environment