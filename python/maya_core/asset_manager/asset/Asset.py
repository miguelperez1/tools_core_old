import os

LIBRARIES_PATH = "F:\\share\\assets\\libraries"

from maya_core.common_tools import logger

log = logger.Logger()


class Asset(object):
    def __init__(self, name, asset_type):
        super(Asset, self).__init__()

        self.name = name
        self.asset_type = asset_type

        self.root_dir = os.path.join(LIBRARIES_PATH, self.asset_type, "{}_root".format(self.name))

        self.maya_dir = os.path.join(self.root_dir, "maya")
        self.maya_file_path = os.path.join(self.maya_dir, "{}.ma".format(self.name))
        self.mesh_dir = os.path.join(self.root_dir, "model")

        self.material_dir = os.path.join(self.root_dir, "material")
        self.textures_dir = os.path.join(self.material_dir, "textures")
        self.textures_path = os.path.join(self.material_dir, "textures")

        self.data_file_path = os.path.join(self.root_dir, "data.json")

        self.proxy_dir = os.path.join(self.root_dir, "vrayproxy")
