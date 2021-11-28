import os
import json
import logging
import string
import subprocess

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm

from maya_core.pipeline.Sequence import Sequence

projects_root = r"F:\share\projects"
default_project_root = os.path.join(projects_root, "default")

logger = logging.getLogger(__name__)
logger.setLevel(10)

SCENES_FOLDER_STRUCTURE = {
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


def create_dirs_from_dict(d, root, parent=None):
    if "subfolders" in d.keys():
        if d['folder_name'] == "top_level":
            _ = [create_dirs_from_dict(a, root, parent=root) for a in d['subfolders']]
        else:
            path = os.path.join(parent, d['folder_name'])

            if not os.path.isdir(path):
                os.mkdir(path)

            _ = [create_dirs_from_dict(a, root, parent=path) for a in d['subfolders']]
    else:
        path = os.path.join(parent, d['folder_name'])

        if not os.path.isdir(path):
            os.mkdir(path)


class Project(object):
    def __init__(self, project_name):
        super(Project, self).__init__()
        self.project_name = project_name
        self.project_path = os.path.join(projects_root, self.project_name).replace("\\", "/")
        self.maya_path = os.path.join(self.project_path, "maya").replace("\\", "/")
        self.scenes_path = os.path.join(self.maya_path, 'scenes')
        self.seq_path = os.path.join(self.scenes_path, "seq")
        self.assets_path = os.path.join(self.scenes_path, "assets")

    def project_exists(self):
        return os.path.isfile(os.path.join(self.maya_path, "workspace.mel"))

    def create_maya_project(self):
        if self.project_exists():
            return

        os.mkdir(os.path.join(projects_root, self.project_name))

        cmds.workspace(self.maya_path, n=1)

        for file_rule in cmds.workspace(query=True, fileRuleList=True):
            file_rule_dir = cmds.workspace(fileRuleEntry=file_rule)
            maya_file_rule_dir = os.path.join(self.maya_path, file_rule_dir)

            if os.path.exists(maya_file_rule_dir):
                continue

            os.makedirs(maya_file_rule_dir)

            set_maya_project(self.maya_path)

        self.create_directories()
        self.create_sequence({'000': ['000']})

        set_maya_project(self.maya_path)
        cmds.workspace(s=1)

        if os.path.exists(os.path.join(self.maya_path, "workspace.mel")):
            logger.info("Created project %s workspace", self.project_name)
        else:
            logger.error("Failed to create project %s workspace", self.project_name)

    def create_directories(self):
        # Project directories
        project_structure_json_path = r"F:\share\tools\tools_core\python\maya_core\pipeline\project\project_directory_structure.json"

        json_file = open(project_structure_json_path, "r")
        project_structure_data = json.load(json_file)
        json_file.close()

        create_dirs_from_dict(project_structure_data, self.project_path)

        # Maya directories
        if os.path.isdir(os.path.join(self.scenes_path, "edits")):
            os.rmdir(os.path.join(self.scenes_path, "edits"))

        for folder, subfolders_data in SCENES_FOLDER_STRUCTURE.items():
            os.mkdir(os.path.join(self.scenes_path, folder))

            for sf, sfsf in subfolders_data.items():
                os.mkdir(os.path.join(self.scenes_path, folder, sf))

                for f in sfsf:
                    os.mkdir(os.path.join(self.scenes_path, folder, sf, f))

        os.mkdir(os.path.join(self.maya_path, "sourceimages", "assets"))

        for asset_type in SCENES_FOLDER_STRUCTURE['assets'].keys():
            source_image_path = os.path.join(self.maya_path, "sourceimages", "assets", asset_type)
            os.mkdir(source_image_path)

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
    proj = Project(project_name)

    if not proj.project_exists():
        return

    project_root = proj.maya_path

    cmds.workspace(project_root, o=1)
    cmds.workspace(dir=project_root)

    mel.eval('setProject \"' + project_root + '\"')

    cmds.autoSave(en=1, dst=0, int=1800)

    if get_current_project().project_name == project_root.split("/")[-2]:
        logger.info("Project set to %s", project_root.split("/")[-2])

        return get_current_project()


def get_current_project():
    return Project(cmds.workspace(sn=1).split("/")[-2])


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
