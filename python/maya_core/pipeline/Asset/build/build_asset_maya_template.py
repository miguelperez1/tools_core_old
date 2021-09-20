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

logger = logging.getLogger(__name__)
logger.setLevel(10)


def create_world_node_file(asset_data):
    cmds.file(f=True, new=True)

    proj = maya_project.get_current_project()

    asset_name = asset_data['asset_name']
    asset_type = asset_data['asset_type']

    asset_root_path = os.path.join(proj.assets_path, asset_type, asset_name[0].lower(), asset_name)
    asset_maya_path = os.path.join(asset_root_path, 'build', 'world_node', '{}.ma'.format(asset_name))

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
    asset_maya_path = os.path.join(asset_root_path, 'build', 'wip', '{}_v001.ma'.format(asset_name))

    cmds.file(rename=os.path.join(asset_maya_path))

    # Reference world node
    world_node_file_path = os.path.join(asset_root_path, 'build', 'world_node', '{}.ma'.format(asset_name))

    cmds.file(world_node_file_path, r=True, ignoreVersion=True, force=True, namespace=asset_name)

    cmds.file(save=True, type="mayaAscii")

    asset_utils.publish_asset_stage(asset_data, 'build', 'v001')

    src = asset_maya_path
    dst = os.path.join(asset_root_path, 'build', "publish", "{}.ma".format(asset_name))

    copyfile(src, dst)

    # TODO Publish Class for Master
    master_path = os.path.join(asset_root_path, "{}.ma".format(asset_name))

    copyfile(dst, master_path)


def create_asset_json(asset_data):
    proj = maya_project.get_current_project()

    asset_name = asset_data['asset_name']
    asset_type = asset_data['asset_type']

    asset_root_path = os.path.join(proj.assets_path, asset_type, asset_name[0].lower(), asset_name)

    asset_json_path = os.path.join(asset_root_path, "data", "data.json")

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
