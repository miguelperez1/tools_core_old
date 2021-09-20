# Publish a wip file to publish for model
# Things that need to be updated
#   The world node must have an attribute for every stage being published
#   add model attribute to world node and set it to current file version number

import os
import re
import logging
from shutil import copyfile

import maya.cmds as cmds
import pymel.core as pm

from maya_core.pipeline.project import maya_project
from maya_core.pipeline.Asset import asset_utils

logger = logging.getLogger(__name__)
logger.setLevel(10)


def publish_model(world_node):
    proj = maya_project.get_current_project()

    asset_name = world_node.assetName.get()
    asset_type = world_node.assetType.get()

    asset_root_path = os.path.join(proj.assets_path, asset_type, asset_name[0].lower(), asset_name)

    file_path = cmds.file(q=True, sn=True).replace("\\", "/")
    file_name = file_path.split("/")[-1]

    version_number = list(set(re.findall("v\d{3}.ma$", file_name)))[0].replace(".ma", "")

    # Update world_node to include the model attribute with the current version number

    if not hasattr(world_node, "buildModel"):
        cmds.addAttr(str(world_node), ln="buildModel", dt="string")

    world_node.buildModel.set(version_number)

    logger.info("Asset world node buildModel version set to: %s", version_number)

    # Save file to publish folder

    publish_file_path = os.path.join(asset_root_path, "model", "publish", "{}.ma".format(asset_name))

    cmds.file(save=True, type="mayaAscii")

    if os.path.isfile(publish_file_path):
        os.remove(publish_file_path)

    copyfile(file_path, publish_file_path)

    if os.path.isfile(publish_file_path):
        logger.info("Published model file successfully")

    asset_data = {
        'asset_name': asset_name,
        'asset_type': asset_type
    }

    asset_utils.publish_asset_stage(asset_data, 'model', version_number)
