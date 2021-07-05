import os

import maya.cmds as cmds

from maya_core.pipeline.project import maya_project


def create_seq(seq_num=None, shots=None):
    current_project = maya_project.get_current_project()
    project_root = os.path.join(maya_project.projects_root, current_project)

    if seq_num:
        os.mkdir(os.path.join(project_root, "scenes", "seq", seq_num))

        if shots:
            for i in range(shots):
                create_shot(i)


def create_shot(shot_num=None):
    pass
