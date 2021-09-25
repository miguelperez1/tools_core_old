import os
import sys
import json
import logging
from shutil import copyfile

import maya.cmds as cmds
import pymel.core as pm

from maya_core.pipeline.project import maya_project
from maya_core.pipeline.Asset import asset_utils

logger = logging.getLogger(__name__)
logger.setLevel(10)

STAGES = ['build', 'model', 'lookdev', 'hair', 'rig', 'dress', 'lighting']


def update_world_node(asset_name, asset_type, stage, version):
    proj = maya_project.get_current_project()

    asset_root_path = os.path.join(proj.assets_path, asset_type, asset_name[0].lower(), asset_name)

    world_node_path = os.path.join(asset_root_path, "01_build", "world_node", "{}.ma".format(asset_name))

    if not os.path.isfile(world_node_path):
        logger.error("Cannot find world node file")
        return

    # open the file
    cmds.file(world_node_path, open=True, ignoreVersion=True, force=True)

    # grab the node
    world_node = pm.PyNode(asset_name)

    # Check for stage attr, add if it doesn't exist
    if not hasattr(world_node, "build{}".format(stage.capitalize())):
        cmds.addAttr(str(world_node), ln="build{}".format(stage.capitalize()), dt="string")

    getattr(world_node, "build{}".format(stage.capitalize())).set(version)

    logger.info("Updated world node %s to %s", stage, version)

    # save file
    cmds.file(save=True, type="mayaAscii")


if __name__ == '__main__':
    asset_stage_data = sys.argv[-1].split(" ")
    asset_name = asset_stage_data[0]
    asset_type = asset_stage_data[1]
    stage = asset_stage_data[2]
    version = asset_stage_data[3]
    project = asset_stage_data[4]

    maya_project.set_maya_project(project)

    update_world_node(asset_name, asset_type, stage, version)

    sys.exit()
