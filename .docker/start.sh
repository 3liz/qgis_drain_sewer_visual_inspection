#!/usr/bin/env bash

docker-compose up -d --force-recreate
echo 'Wait 10 seconds'
sleep 10
echo 'Installation of the plugin'
docker exec -it qgis sh -c "qgis_setup.sh drain_sewer_visual_inspection"
echo 'Containers are running'
