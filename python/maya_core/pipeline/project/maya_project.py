import os
import json
import logging

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm

from maya_core.common_tools.get_input import get_input
from maya_core.pipeline.Sequence import Sequence

projects_root = r"F:\share\projects"
default_project_root = os.path.join(projects_root, "default")

logger = logging.getLogger(__name__)
logger.setLevel(10)


class Project(object):
    def __init__(self, project_name):
        super(Project, self).__init__()
        self.project_name = project_name
        self.project_root = os.path.join(projects_root, self.project_name).replace("\\", "/")
        self.seq_root = os.path.join(self.project_root, "scenes", "seq")
        self.asset_root = os.path.join(self.project_root, "scenes", "asset")

        # globals

    def project_exists(self):
        return os.path.isfile(os.path.join(self.project_root, "workspace.mel"))

    def create_maya_project(self):
        cmds.workspace(self.project_root, n=1)

        for file_rule in cmds.workspace(query=True, fileRuleList=True):
            file_rule_dir = cmds.workspace(fileRuleEntry=file_rule)
            maya_file_rule_dir = os.path.join(self.project_root, file_rule_dir)

            if os.path.exists(maya_file_rule_dir):
                continue

            os.makedirs(maya_file_rule_dir)

            set_maya_project(self.project_root)

        os.mkdir(self.asset_root)
        os.mkdir(self.seq_root)

        set_maya_project(self.project_root)
        cmds.workspace(s=1)

        if os.path.exists(os.path.join(self.project_root, "workspace.mel")):
            logger.info("Created project %s workspace", self.project_name)
        else:
            logger.error("Failed to create project %s workspace", self.project_name)

        self.create_sequence()

    def get_assets(self):
        pass

    def get_timeline(self):
        pass

    def create_sequence(self, seq_data=None):
        if not seq_data:
            seq_data = {
                "000": [
                    '000'
                ]
            }

        for seq, shots in seq_data.items():
            new_seq = Sequence.Sequence(self, seq, shots)
            new_seq.create_sequence()


def set_maya_project(project_root):
    project_root = project_root.replace("\\", "/")
    cmds.workspace(project_root, o=1)
    cmds.workspace(dir=project_root)

    mel.eval('setProject \"' + project_root + '\"')

    cmds.autoSave(en=1, dst=0, int=1800)

    if get_current_project().project_name == project_root.split("/")[-1]:
        logger.info("Project set to %s", project_root.split("/")[-1])


def get_current_project():
    return Project(cmds.workspace(sn=1).split("/")[-1])
