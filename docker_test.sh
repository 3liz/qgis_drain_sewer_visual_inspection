docker run -d --name qgis-testing-environment -v ${PWD}:/qgis_drain_sewer_visual_inspection -e DISPLAY=:99 qgis/qgis:release-3_4
sleep 10
docker exec -it qgis-testing-environment sh -c "qgis_setup.sh qgis_drain_sewer_visual_inspection"
docker exec -it qgis-testing-environment sh -c "qgis_testrunner.sh qgis_drain_sewer_visual_inspection.test_runner.test_package"
status=$?
docker stop qgis-testing-environment
docker rm qgis-testing-environment
exit ${status}
