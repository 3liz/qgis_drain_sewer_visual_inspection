"""Processing provider."""

from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsProcessingProvider

from .config_project_algorithm import ConfigProjectAlgorithm
from .create_geom_obs_algorithm import CreateGeomObsAlgorithm
from .create_geom_segment_algorithm import CreateGeomTronconAlgorithm
from .create_data_model_algorithm import CreatePostgisTables, CreateGeopackage
from .load_postgis_layers_algorithm import LoadPostgisTables
from .import_dsvi_file_algorithm import ImportDsviFileAlgorithm
from .import_geom_regard_algorithm import ImportGeomRegardAlgorithm
from ..qgis_plugin_tools.tools.i18n import tr
from ..qgis_plugin_tools.tools.resources import resources_path

# from .create_temp_geom_troncon_algorithm import CreateTempGeomTronconAlgorithm
# from .create_temp_geom_obs_algorithm import CreateTempGeomObsAlgorithm

__copyright__ = "Copyright 2019, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = '$Format:%H$'


class Provider(QgsProcessingProvider):

    def loadAlgorithms(self):
        """
        Loads all algorithms belonging to this provider.
        """
        # The order is more or less the workflow
        self.addAlgorithm(CreateGeopackage())
        self.addAlgorithm(CreatePostgisTables())
        self.addAlgorithm(LoadPostgisTables())
        self.addAlgorithm(ConfigProjectAlgorithm())
        self.addAlgorithm(ImportGeomRegardAlgorithm())
        self.addAlgorithm(ImportDsviFileAlgorithm())
        self.addAlgorithm(CreateGeomTronconAlgorithm())
        self.addAlgorithm(CreateGeomObsAlgorithm())

        # self.addAlgorithm(CreateTempGeomTronconAlgorithm())
        # self.addAlgorithm(CreateTempGeomObsAlgorithm())

    def icon(self):
        return QIcon(resources_path('icons', 'icon.png'))

    # def svgIconPath(self):
    #     return resources_path('icons', 'icon.svg')

    def id(self):
        return 'drain_sewer_visual_inspection'

    def name(self):
        return tr('Drain sewer visual inspection')

    def longName(self):
        return self.name()
