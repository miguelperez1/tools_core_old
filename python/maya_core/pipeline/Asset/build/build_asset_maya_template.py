import os
import sys
import json
import logging
from shutil import copyfile


import maya.standalone as standalone

standalone.initialize(name='python')

import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel

from maya_core.pipeline.Asset import MayaAsset
from maya_core.pipeline.project import maya_project
from maya_core.pipeline.Asset import asset_utils
from maya_core.pipeline.Asset.publish import publish_stage

logger = logging.getLogger(__name__)
logger.setLevel(10)


def create_world_node_file(asset_data):
    cmds.file(f=True, new=True)

    proj = maya_project.get_current_project()

    asset_name = asset_data['asset_name']
    asset_type = asset_data['asset_type']

    asset_root_path = os.path.join(proj.assets_path, asset_type, asset_name[0].lower(), asset_name)
    asset_maya_path = os.path.join(asset_root_path, '01_build', 'world_node', '{}.ma'.format(asset_name))

    cmds.file(rename=os.path.join(asset_maya_path))

    asset_node = MayaAsset.MayaAsset(asset_data=asset_data)

    cmds.file(save=True, type="mayaAscii")

    if os.path.isfile(asset_maya_path) and pm.objExists(asset_node.world_node):
        logger.info("Successfully built %s maya file", asset_name)


def create_build(asset_data):
    # Create initial v001 wip file
    cmds.file(f=True, new=True)

    proj = maya_project.get_current_project()

    asset_name = asset_data['asset_name']
    asset_type = asset_data['asset_type']

    asset_root_path = os.path.join(proj.assets_path, asset_type, asset_name[0].lower(), asset_name)
    asset_maya_path = os.path.join(asset_root_path, '01_build', 'wip', '{}_build_v001.ma'.format(asset_name))

    cmds.file(rename=os.path.join(asset_maya_path))

    # Reference world node
    world_node_file_path = os.path.join(asset_root_path, '01_build', 'world_node', '{}.ma'.format(asset_name))

    cmds.file(world_node_file_path, i=True, ignoreVersion=True, force=True, namespace=asset_name)

    cmds.file(save=True, type="mayaAscii")

    world_node = pm.PyNode("{0}:{0}".format(asset_name))

    if world_node is None or (world_node is not None and not hasattr(world_node, "mayaAsset")):
        logger.error("%s world node not found", asset_name)
        return

    publish_stage.publish_stage(world_node, 'build', 'v001')


def create_asset_json(asset_data):
    proj = maya_project.get_current_project()

    asset_name = asset_data['asset_name']
    asset_type = asset_data['asset_type']

    asset_root_path = os.path.join(proj.assets_path, asset_type, asset_name[0].lower(), asset_name)

    asset_json_path = os.path.join(asset_root_path, "00_data", "data.json")

    publish_assset_data = {
        'asset_name': asset_name,
        'asset_type': asset_type,
        'stages': {}
    }

    with open(asset_json_path, "w") as f:
        json.dump(publish_assset_data, f, indent=4, sort_keys=True)


if __name__ == '__main__':
    asset_build_data = sys.argv[-1].split(" ")
    current_project = asset_build_data[0]
    asset_name = asset_build_data[1]
    asset_type = asset_build_data[2]

    asset_data = {
        'asset_name': asset_name,
        'asset_type': asset_type
    }

    maya_project.set_maya_project(current_project)

    create_asset_json(asset_data)

    create_world_node_file(asset_data)
    create_build(asset_data)

    sys.exit()
