# Drain sewer visual inspection

QGIS plugin for drain and sewer systems visual inspection coding system (EN 13508-2)

The documentation is available on [docs.3liz.org](https://3liz.github.io/qgis_drain_sewer_visual_inspection/).

* Travis status : [![Travis status](https://api.travis-ci.org/3liz/qgis_drain_sewer_visual_inspection.svg?branch=master)](https://travis-ci.org/3liz/qgis_drain_sewer_visual_inspection)
* For testing with private confidential data, drop the ITV txt file into `test/data/confidential`

### SQL

Add relationships for Schemaspy:

```sql
ALTER TABLE sewer.obs ADD CONSTRAINT file_obs FOREIGN KEY (id_file) REFERENCES sewer.file (id);
ALTER TABLE sewer.regard ADD CONSTRAINT file_regard FOREIGN KEY (id_file) REFERENCES sewer.file (id);
ALTER TABLE sewer.troncon ADD CONSTRAINT file_troncon FOREIGN KEY (id_file) REFERENCES sewer.file (id);
ALTER TABLE sewer.regard ADD CONSTRAINT regard_geom_regard FOREIGN KEY (id_geom_regard) REFERENCES sewer.geom_regard (id);
ALTER TABLE sewer.troncon ADD CONSTRAINT troncon_geom_troncon FOREIGN KEY (id_geom_troncon) REFERENCES sewer.geom_troncon (id);
ALTER TABLE sewer.obs ADD CONSTRAINT troncon_observation FOREIGN KEY (id_troncon) REFERENCES sewer.troncon (id);
-- TOCHECK FILE - GEOMS OBS
```
