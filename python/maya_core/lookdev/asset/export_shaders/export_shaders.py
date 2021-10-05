import os
import json
import logging

import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel

from maya_core.pipeline.project import maya_project
from maya_core.lookdev.material_utils import material_utils as mu

# Create a json file where
#   Key (Mesh node) : Value (Material)
#   Export a .ma file with all materials


# Rigging / Lighting will then run the apply
logger = logging.getLogger(__name__)
logger.setLevel(10)


def export_shaders(asset_node):
    if not hasattr(asset_node, "mayaAsset"):
        logger.error("Node is not an asset node.")
        return

    geo_group = pm.PyNode(("{}|Geometry|HiRes|Constrain|GEO".format(str(asset_node))))

    asset_name = asset_node.assetName.get()
    asset_type = asset_node.assetType.get()
    lookdev_version = asset_node.buildLookdev.get()

    asset_root_path = os.path.join(maya_project.get_current_project().assets_path, asset_type, asset_name[0].lower(),
                                   asset_name)

    lookdev_publish_json_path = os.path.join(asset_root_path, "03_lookdev", "publish", "shaders.json")

    shader_data = {
        "buildLookdev": lookdev_version,
        "shaders": {}
    }

    meshes = [m.longName() for m in geo_group.listRelatives(ad=1, type="mesh") if
              not str(m).startswith("polySurfaceShape")]

    for mesh in meshes:
        sg = mu.get_materials(mesh).keys()[0]
        shader_data["shaders"][mesh] = sg.longName()

    with open(lookdev_publish_json_path, "w") as f:
        json.dump(shader_data, f, indent=4, sort_keys=True)

    shaders_path = lookdev_publish_json_path.replace(".json", ".ma")

    shaders = []
    for mesh, shading_group in shader_data["shaders"].items():
        if pm.nodeType(shading_group) == "shadingEngine":
            shaders.append(shading_group)

    pm.select(cl=1)

    pm.select(shaders, ne=1)

    pm.exportSelected(shaders_path, type="mayaAscii", channels=0, force=True, preserveReferences=False)

    if os.path.isfile(lookdev_publish_json_path) and os.path.isfile(shaders_path):
        logger.debug(shader_data)
        logger.info("Published %s shaders", asset_name)
