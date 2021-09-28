import os
import json
import logging
import string
import subprocess


def create_dirs_from_dict(d, asset_root, parent=None):
    if "subfolders" in d.keys():
        if d['folder_name'] == "top_level":
            _ = [create_dirs_from_dict(a, asset_root, parent=asset_root) for a in d['subfolders']]
        else:
            path = os.path.join(parent, d['folder_name'])

            if not os.path.isdir(path):
                os.mkdir(path)

            _ = [create_dirs_from_dict(a, asset_root, parent=path) for a in d['subfolders']]
    else:
        path = os.path.join(parent, d['folder_name'])

        if not os.path.isdir(path):
            os.mkdir(path)


class Asset(object):
    def __init__(self, asset_name, asset_type, project):
        self.asset_name = asset_name.replace(" ", "_")
        self.asset_type = asset_type.lower()
        self.project = project

        self.asset_root_path = os.path.join(self.project.assets_path, self.asset_type, asset_name[0].lower(),
                                            self.asset_name).replace("\\", "/")

    def create_asset(self):
        # create letter directory if it doesn't exist
        letter_path = "/".join(self.asset_root_path.split("/")[:-1])

        if not os.path.isdir(letter_path):
            os.mkdir(letter_path)

        # create asset root path
        os.mkdir(self.asset_root_path)

        # Create asset directories
        asset_structure_json_path = r"F:\share\tools\tools_core\python\maya_core\pipeline\Asset\asset_directory_structure.json"

        json_file = open(asset_structure_json_path, "r")
        asset_structure_data = json.load(json_file)
        json_file.close()

        create_dirs_from_dict(asset_structure_data, self.asset_root_path)

        # Create asset sourceimages folder
        if not os.path.isdir(letter_path.replace("scenes", "sourceimages")):
            os.mkdir(letter_path.replace("scenes", "sourceimages"))

        os.mkdir(os.path.join(letter_path.replace("scenes", "sourceimages"), self.asset_name))

        function = r'F:\share\tools\tools_core\python\maya_core\pipeline\Asset\build\build_asset_maya_template.py'

        arg = '{0} {1} {2}'.format(self.project.project_name, self.asset_name, self.asset_type)

        log_path = os.path.join(self.asset_root_path, '00_data', 'logs', "initial_build_log.txt")
        f = open(log_path, "w")

        subprocess.call(['mayapy', function, arg], stdout=f, stderr=subprocess.STDOUT)

        if os.path.isfile(os.path.join(self.asset_root_path, "{}.ma".format(self.asset_name))):
            print("{} created successfully".format(self.asset_name))
