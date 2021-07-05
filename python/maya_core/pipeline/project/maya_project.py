import os
import json
import logging

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm

from maya_core.common_tools.get_input import get_input

projects_root = r"F:\share\projects"
default_project_root = os.path.join(projects_root, "default")

logger = logging.getLogger(__name__)
logger.setLevel(10)


def create_maya_project(project_name):
    project_root = os.path.join(projects_root, project_name).replace("\\", "/")

    cmds.workspace(project_root, n=1)

    for file_rule in cmds.workspace(query=True, fileRuleList=True):
        file_rule_dir = cmds.workspace(fileRuleEntry=file_rule)
        maya_file_rule_dir = os.path.join(project_root, file_rule_dir)

        if os.path.exists(maya_file_rule_dir):
            continue

        os.makedirs(maya_file_rule_dir)

        set_maya_project(project_root)

    asset_dir = os.path.join(project_root, "scenes", "asset")
    seq_dir = os.path.join(project_root, "scenes", "seq")

    os.mkdir(asset_dir)
    os.mkdir(seq_dir)

    set_maya_project(project_root)
    cmds.workspace(s=1)

    if os.path.exists(os.path.join(project_root, "workspace.mel")):
        logger.info("Created %s", project_name)
    else:
        logger.error("Project %s not created", project_name)


def set_maya_project(project_root):
    project_root = project_root.replace("\\", "/")
    cmds.workspace(project_root, o=1)
    cmds.workspace(dir=project_root)

    mel.eval('setProject \"' + project_root + '\"')

    cmds.autoSave(en=1, dst=0, int=300)

    if get_current_project() == project_root.split("/")[-1]:
        logger.info("Project set to %s", project_root.split("/")[-1])


def get_current_project():
    return cmds.workspace(sn=1).split("/")[-1]
