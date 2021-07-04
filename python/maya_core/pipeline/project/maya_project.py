import os
import json

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm

from maya_core.common_tools.get_input import get_input

projects_root = r"F:\share\projects"
default_project_root = os.path.join(projects_root, "default")


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

    set_maya_project(project_root)
    cmds.workspace(s=1)


def set_maya_project(project_root):
    project_root = project_root.replace("\\", "/")
    cmds.workspace(project_root, o=1)
    cmds.workspace(dir=project_root)
    mel.eval('setProject \"' + project_root + '\"')


def get_current_project():
    return cmds.workspace(sn=1).split("/")[-1]
