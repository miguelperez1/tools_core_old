import os
import json
import logging
import string
import subprocess

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm

from maya_core.common_tools.get_input import get_input
from maya_core.pipeline.Sequence import Sequence

projects_root = r"F:\share\projects"
default_project_root = os.path.join(projects_root, "default")

logger = logging.getLogger(__name__)
logger.setLevel(10)

PROJECT_FOLDER_STRUCTURE = {
    'seq': {},
    'assets': {
        'character': [],
        'prop': [],
        'set': [],
        'transit': [],
        'lighting': [],
        'cameras': [],
        'rig': []
    },
    'data': {
        'logs': []
    },
    'rnd': {},
    'testing': {}
}

ASSET_FOLDER_STRUCTURE = {
    '00_data': {
        'logs': []
    },
    '01_build': {
        'publish': [],
        'world_node': [],
        'wip': []
    },
    '02_model': {
        'wip': [],
        'publish': []
    },
    '03_lookdev': {
        'wip': [],
        'publish': []
    },
    '04_hair': {
        'xgen': [],
        'cahe': [],
        'wip': [],
        'publish': []
    },
    '05_rig': {
        'publish': [],
        'wip': []
    },
    '06_dress': {
        'wip': [],
        'publish': []
    },
    '07_lighting': {
        'wip': [],
        'publish': []
    },
    '99_cache': {}

}


class Project(object):
    def __init__(self, project_name):
        super(Project, self).__init__()
        self.project_name = project_name
        self.project_path = os.path.join(projects_root, self.project_name).replace("\\", "/")
        self.scenes_path = os.path.join(self.project_path, 'scenes')
        self.seq_path = os.path.join(self.scenes_path, "seq")
        self.assets_path = os.path.join(self.scenes_path, "assets")

    def project_exists(self):
        return os.path.isfile(os.path.join(self.project_path, "workspace.mel"))

    def create_maya_project(self):
        if self.project_exists():
            return

        cmds.workspace(self.project_path, n=1)

        for file_rule in cmds.workspace(query=True, fileRuleList=True):
            file_rule_dir = cmds.workspace(fileRuleEntry=file_rule)
            maya_file_rule_dir = os.path.join(self.project_path, file_rule_dir)

            if os.path.exists(maya_file_rule_dir):
                continue

            os.makedirs(maya_file_rule_dir)

            set_maya_project(self.project_path)

        self.create_directories()
        self.create_sequence({'000': ['000']})

        set_maya_project(self.project_path)
        cmds.workspace(s=1)

        if os.path.exists(os.path.join(self.project_path, "workspace.mel")):
            logger.info("Created project %s workspace", self.project_name)
        else:
            logger.error("Failed to create project %s workspace", self.project_name)

    def create_directories(self):
        if os.path.isdir(os.path.join(self.scenes_path, "edits")):
            os.rmdir(os.path.join(self.scenes_path, "edits"))

        for folder, subfolders_data in PROJECT_FOLDER_STRUCTURE.items():
            os.mkdir(os.path.join(self.scenes_path, folder))

            for sf, sfsf in subfolders_data.items():
                os.mkdir(os.path.join(self.scenes_path, folder, sf))

                for f in sfsf:
                    os.mkdir(os.path.join(self.scenes_path, folder, sf, f))

    def get_assets(self):
        assets_data = {}
        all_assets = []

        for asset_type in os.listdir(self.assets_path.replace("\\", "/")):
            assets_data[asset_type] = []

            for letter in os.listdir(os.path.join(self.assets_path, asset_type)):
                for asset in os.listdir(os.path.join(self.assets_path, asset_type, letter)):
                    assets_data[asset_type].append(asset)
                    all_assets.append(asset)

        return assets_data, all_assets

    def get_timeline(self):
        pass

    def create_asset(self, asset_name, asset_type):
        if asset_name in self.get_assets()[-1]:
            return

        asset_name = asset_name.replace(" ", "_")

        asset_letter_path = os.path.join(self.assets_path, asset_type, asset_name[0].lower())

        if not os.path.isdir(asset_letter_path):
            os.mkdir(asset_letter_path)

        asset_root_path = os.path.join(asset_letter_path, asset_name)

        if not os.path.isdir(asset_root_path):
            os.mkdir(asset_root_path)

            for folder, subfolders_data in ASSET_FOLDER_STRUCTURE.items():
                os.mkdir(os.path.join(asset_root_path, folder))

                for sf, sfsf in subfolders_data.items():
                    os.mkdir(os.path.join(asset_root_path, folder, sf))

                    for f in sfsf:
                        os.mkdir(os.path.join(asset_root_path, folder, sf, f))

        function = r'F:\share\tools\tools_core\python\maya_core\pipeline\Asset\build\build_asset_maya_template.py'

        arg = '{0} {1} {2}'.format(self.project_name, asset_name, asset_type)

        log_path = os.path.join(asset_root_path, '00_data', 'logs', "build_log.txt")
        f = open(log_path, "w")

        subprocess.call(['mayapy', function, arg], stdout=f, stderr=subprocess.STDOUT)

        if os.path.isfile(os.path.join(asset_root_path, "{}.ma".format(asset_name))):
            logger.info("Built %s successfully", asset_name)
        else:
            logger.error("Asset not built")

    def create_sequence(self, seq_data):
        for seq, shots in seq_data.items():
            new_seq = Sequence.Sequence(self, seq, shots)
            new_seq.create_sequence()

    def get_asset(self, asset_name):
        for asset_type, assets in self.get_assets()[0].items():
            for asset in assets:
                if asset_name == asset:
                    return asset_name, asset_type


def set_maya_project(project_name):
    project_root = os.path.join(projects_root, project_name)

    if not os.path.isdir(project_root):
        return

    project_root = project_root.replace("\\", "/")
    cmds.workspace(project_root, o=1)
    cmds.workspace(dir=project_root)

    mel.eval('setProject \"' + project_root + '\"')

    cmds.autoSave(en=1, dst=0, int=1800)

    if get_current_project().project_name == project_root.split("/")[-1]:
        logger.info("Project set to %s", project_root.split("/")[-1])


def get_current_project():
    return Project(cmds.workspace(sn=1).split("/")[-1])


def get_all_projects():
    projects = []
    for project in os.listdir(projects_root):
        if project == 'archive' or not os.path.isdir(os.path.join(projects_root, project)):
            continue
        else:
            projects.append(Project(project))

    return projects


def get_project(project_name):
    for p in get_all_projects():
        if p.project_name == project_name:
            return p
