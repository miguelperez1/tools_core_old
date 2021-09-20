import os

import maya.cmds as cmds
import pymel.core as pm

from maya_core.pipeline.project import maya_project
from maya_core.pipeline.Asset import asset_utils


def build_world_node(world_node):
    proj = maya_project.get_current_project()

    asset_type = world_node.assetType.get()
    asset_name = world_node.assetName.get()

    tmp_asset_data = {
        'asset_type': asset_type,
        'asset_name': asset_name
    }

    # Get stages being used
    asset_data = asset_utils.get_asset_data(tmp_asset_data)

    for stage, version in asset_data['stages']:
        # Set world node to use stage and version

        pass
        # Run each build stage
