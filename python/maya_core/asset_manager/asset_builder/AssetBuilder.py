import os
import json
from shutil import copyfile
import subprocess

from maya_core.asset_manager.asset import Asset

from maya_core.common_tools import logger
from maya_core import asset_manager
from maya_core.asset_manager import asset

log = logger.Logger()
log.status = True

reload(asset)
reload(asset_manager)


class AssetBuilder(object):
    def __init__(self, data):
        super(AssetBuilder, self).__init__()
        self.data = data
        self.asset = asset.Asset(self.data["name"], self.data["type"])

        # Create Directories
        self.create_directories()

        # Create data json
        self.create_json_file()

        # Copy Preview
        if self.data["preview"]:
            file_ext = self.data["preview"].split('.')[-1]
            preview_dst = self.asset.root_dir + '\\{0}_preview.{1}'.format(self.asset.name, file_ext)
            copyfile(self.data["preview"], preview_dst)

        self.create_maya()

        asset_manager.build_asset_library()

    def create_directories(self):
        # root
        os.mkdir(self.asset.root_dir)
        if os.path.isdir(self.asset.root_dir):
            log.debug("Created {}".format(self.asset.root_dir))

        os.mkdir(self.asset.maya_dir)
        if os.path.isdir(self.asset.maya_dir):
            log.debug("Created {}".format(self.asset.maya_dir))

        os.mkdir(self.asset.material_dir)
        if os.path.isdir(self.asset.material_dir):
            log.debug("Created {}".format(self.asset.material_dir))

        os.mkdir(self.asset.textures_dir)
        if os.path.isdir(self.asset.textures_dir):
            log.debug("Created {}".format(self.asset.textures_dir))

        if self.data["has_proxy"]:
            os.mkdir(self.asset.proxy_dir)
            if os.path.isdir(self.asset.proxy_dir):
                log.debug("Created {}".format(self.asset.proxy_dir))

        if self.data["mesh"]:
            os.mkdir(os.path.join(self.asset.root_dir, "model"))
            if os.path.isdir(os.path.join(self.asset.root_dir, "model")):
                log.debug("Created {}".format(os.path.join(self.asset.root_dir, "model")))

    def create_json_file(self):
        with open(self.asset.data_file_path, "w") as f:
            json.dump(self.data, f, indent=4, sort_keys=True)

        if os.path.isfile(self.asset.data_file_path):
            log.debug("Created {}".format(self.asset.data_file_path))

    def create_maya(self):
        function = r'F:\share\tools\tools_core\python\maya_core\asset_manager\asset_builder\maya_builder.py'
        arg = '{}'.format(self.asset.data_file_path)

        log.debug("Launching Maya subprocess...")

        log_path = os.path.join(self.asset.root_dir, "build_log.txt")
        f = open(log_path, "w")

        subprocess.call(['mayapy', function, arg], stdout=f, stderr=subprocess.STDOUT)

        if os.path.isfile(self.asset.maya_file_path):
            log.debug("Created maya file")
        else:
            log.debug("Maya file was not created")
