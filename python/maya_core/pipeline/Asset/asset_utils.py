import os
import json
import logging

import maya.cmds as cmds
import pymel.core as pm

from maya_core.pipeline.project import maya_project
from maya_core.pipeline.Asset.MayaAsset import MayaAsset

logger = logging.getLogger(__name__)
logger.setLevel(10)

STAGES = ['build', 'model', 'lookdev', 'hair', 'rig', 'dress', 'lighting']


def get_all_asset_nodes():
    asset_nodes = []

    for n in pm.ls(assemblies=1):
        if hasattr(n, "mayaAsset"):
            asset_node = MayaAsset(node=n)
            asset_nodes.append(asset_node)

    return asset_nodes


def get_asset_data(asset_data):
    proj = maya_project.get_current_project()

    asset_name = asset_data['asset_name']
    asset_type = asset_data['asset_type']

    asset_root_path = os.path.join(proj.assets_path, asset_type, asset_name[0].lower(), asset_name)

    asset_json_path = os.path.join(asset_root_path, '00_data', 'data.json')

    json_file = open(asset_json_path, "r")
    asset_root_data = json.load(json_file)
    json_file.close()

    return asset_root_data
