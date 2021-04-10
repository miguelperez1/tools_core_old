import os

LIBRARIES_PATH = "D:\\share\\assets\\libraries"

class Asset(object):
    def __init__(self, name, type, scale, singular):
        self.name = name
        self.type = type
        self.scale = scale
        self.singular = singular

        self.asset_root_path = LIBRARIES_PATH + "\\{0}\\{1}".format(self.type, self.name)


    def create_dirs(self):
        os.mkdir(self.asset_root_path)
        for root, sub in self.dirs.items():
            os.mkdir(self.asset_root_path + "\\{}".format(root))
            for subroot in sub:
                os.mkdir(self.asset_root_path + "\\{0}\\{1}".format(root, subroot))