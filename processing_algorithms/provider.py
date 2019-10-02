"""Processing provider."""

__copyright__ = "Copyright 2019, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = '$Format:%H$'

from qgis.core import QgsProcessingProvider
from qgis.PyQt.QtGui import QIcon

# from .create_temp_geom_troncon_algorithm import CreateTempGeomTronconAlgorithm
# from .create_geom_troncon_algorithm import CreateGeomTronconAlgorithm
# from .create_temp_geom_obs_algorithm import CreateTempGeomObsAlgorithm
# from .create_geom_obs_algorithm import CreateGeomObsAlgorithm
# from .calc_obs_rerau_algorithm import CalcObsRerauAlgorithm
# from .calc_troncon_rerau_algorithm import CalcTronconRerauAlgorithm
# from .calc_troncon_rerau_classif_algorithm import CalcTronconRerauClassifAlgorithm

from .create_geopackage_algorithm import CreateGeopackageAlgorithm
from .config_project_algorithm import ConfigProjectAlgorithm
from .import_geom_regard_algorithm import ImportGeomRegardAlgorithm
from .import_itv_algorithm import ImportItvAlgorithm


from ..qgis_plugin_tools.resources import resources_path


class Provider(QgsProcessingProvider):

    def loadAlgorithms(self):
        """
        Loads all algorithms belonging to this provider.
        """
        # The order is more or less the workflow
        self.addAlgorithm(CreateGeopackageAlgorithm())
        self.addAlgorithm(ConfigProjectAlgorithm())
        self.addAlgorithm(ImportGeomRegardAlgorithm())
        self.addAlgorithm(ImportItvAlgorithm())
        # self.addAlgorithm(CreateTempGeomTronconAlgorithm())
        # self.addAlgorithm(CreateGeomTronconAlgorithm())
        # self.addAlgorithm(CreateTempGeomObsAlgorithm())
        # self.addAlgorithm(CreateGeomObsAlgorithm())
        # self.addAlgorithm(CalcObsRerauAlgorithm())
        # self.addAlgorithm(CalcTronconRerauAlgorithm())
        # self.addAlgorithm(CalcTronconRerauClassifAlgorithm())

    def icon(self):
        return QIcon(resources_path('icons', 'icon.png'))

    def svgIconPath(self):
        return resources_path('icons', 'icon.svg')

    def id(self):
        """
        Returns the unique provider id, used for identifying the provider. This
        string should be a unique, short, character only string, eg "qgis" or
        "gdal". This string should not be localised.
        """
        return 'drain_sewer_visual_inspection'

    def name(self):
        """
        Returns the provider name, which is used to describe the provider
        within the GUI.

        This string should be short (e.g. "Lastools") and localised.
        """
        return self.tr('Drain sewer visual inspection')

    def longName(self):
        """
        Returns the a longer version of the provider name, which can include
        extra details such as version numbers. E.g. "Lastools LIDAR tools
        (version 2.2.1)". This string should be localised. The default
        implementation returns the same string as name().
        """
        return self.name()
