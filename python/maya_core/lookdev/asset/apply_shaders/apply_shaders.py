import os
import json
import logging

import pymel.core as pm
import maya.cmds as cmds

from maya_core.pipeline.project import maya_project
from maya_core.lookdev.material_utils import material_utils as mu

# Rigging / Lighting will then run the apply
logger = logging.getLogger(__name__)
logger.setLevel(10)


def apply_shaders(shader_data_path=None):
    n = None
    ns = pm.ls(sl=1)

    if ns:
        n = ns[0]

    if not hasattr(n, "mayaAsset"):
        return

    asset_name = n.assetName.get()
    asset_type = n.assetType.get()

    asset_root_path = os.path.join(maya_project.get_current_project().assets_path, asset_type, asset_name[0].lower(),
                                   asset_name)

    if shader_data_path is not None:
        json_file = open(shader_data_path, "r")
        shader_data = json.load(json_file)
        json_file.close()
    else:
        shader_data_path = os.path.join(asset_root_path, "03_lookdev", "publish", "shaders.json")

        if not os.path.isfile(shader_data_path):
            logger.error("Cannot find shaders.json for %s", asset_name)
            return

        json_file = open(shader_data_path, "r")
        shader_data = json.load(json_file)
        json_file.close()

    shader_ma = shader_data_path.replace(".json", ".ma")

    if not os.path.isfile(shader_ma):
        logger.error("Cannot find shaders.ma for %s", asset_name)
        return

    cmds.file(shader_ma, i=1)

    for geo, sg in shader_data["shaders"].items():
        try:
            geo_node = pm.PyNode(geo)
        except Exception as e:
            raise e

        try:
            pm.sets(sg, edit=True, forceElement=geo_node)
        except Exception as e:
            raise e
