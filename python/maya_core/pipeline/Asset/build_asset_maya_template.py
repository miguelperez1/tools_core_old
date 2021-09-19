import os
import sys
import json
import logging

import maya.standalone as standalone

standalone.initialize(name='python')

import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel

from maya_core.pipeline.Asset import MayaAsset
from maya_core.pipeline.project import maya_project

logger = logging.getLogger(__name__)
logger.setLevel(10)

if __name__ == '__main__':
    asset_build_data = sys.argv[-1].split(" ")
    current_project = asset_build_data[0]
    asset_name = asset_build_data[1]
    asset_type = asset_build_data[2]

    cmds.file(f=True, new=True)
    maya_project.set_maya_project(current_project)
    proj = maya_project.get_current_project()

    asset_maya_path = os.path.join(proj.assets_path, asset_type, asset_name[0].lower(), asset_name,
                                   '{}.ma'.format(asset_name))

    cmds.file(rename=os.path.join(asset_maya_path))

    asset_data = {
        'asset_name': asset_name,
        'asset_type': asset_type
    }

    asset_node = MayaAsset.MayaAsset(asset_data=asset_data)

    cmds.file(save=True, type="mayaAscii")

    if os.path.isfile(asset_maya_path) and pm.objExists(asset_node.world_node):
        logger.info("Successfully built %s maya file", asset_name)
