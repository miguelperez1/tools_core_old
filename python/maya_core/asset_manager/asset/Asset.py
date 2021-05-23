import os

LIBRARIES_PATH = "D:\\share\\assets\\libraries"


class Asset(object):
    def __init__(self, asset_name=None, asset_type=None, path=None):
        if path is not None:
            self.root_path = path.replace("/", "\\")
            self.asset_name = self.root_path.split("\\")[-1].split("_root")[0]
            self.asset_type = self.root_path.split("\\")[-2]
            self.textures_path = os.path.join(self.root_path, "textures")
        else:
            self.asset_name = asset_name
            self.asset_type = asset_type
            self.root_path = os.path.join(LIBRARIES_PATH, self.asset_type, "{}_root".format(self.asset_name))
            self.textures_path = os.path.join(self.root_path, "textures")
