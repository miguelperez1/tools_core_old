import os
import re
import json
import time
import subprocess
import logging
from shutil import copyfile

import maya.cmds as cmds
import pymel.core as pm

from maya_core.pipeline.project import maya_project
from maya_core.pipeline.Asset import asset_utils

from maya_core.lookdev.asset.export_shaders import export_shaders

logger = logging.getLogger(__name__)
logger.setLevel(10)

STAGES = ['build', 'model', 'lookdev', 'hair', 'rig', 'dress', 'lighting']


def publish_asset_stage_json(asset_data, stage, version):
    if stage not in STAGES:
        logger.error("Invalid stage")
        return

    proj = maya_project.get_current_project()

    asset_name = asset_data['asset_name']
    asset_type = asset_data['asset_type']

    asset_root_path = os.path.join(proj.assets_path, asset_type, asset_name[0].lower(), asset_name)

    asset_json_path = os.path.join(asset_root_path, '00_data', 'data.json')

    json_file = open(asset_json_path, "r")
    asset_root_data = json.load(json_file)
    json_file.close()

    asset_root_data['stages'][stage] = version

    with open(asset_json_path, "w") as f:
        json.dump(asset_root_data, f, indent=4, sort_keys=True)


def publish_build_to_master(asset_data):
    proj = maya_project.get_current_project()

    asset_name = asset_data['asset_name']
    asset_type = asset_data['asset_type']

    asset_root_path = os.path.join(proj.assets_path, asset_type, asset_name[0].lower(), asset_name)

    build_publish_file = os.path.join(asset_root_path, "01_build", "publish", "{}_build.ma".format(asset_name))

    if not os.path.isfile(build_publish_file):
        logger.error("Could not find published build file")
        return

    master_file_path = os.path.join(asset_root_path, "{}.ma".format(asset_name))

    if os.path.isfile(master_file_path):
        os.remove(master_file_path)

    copyfile(build_publish_file, master_file_path)


def publish_stage(world_node, stage, version=None):
    if stage not in STAGES:
        logger.error("%s is not a stage", stage)
        return

    stage = stage.capitalize()

    proj = maya_project.get_current_project()

    asset_name = world_node.assetName.get()
    asset_type = world_node.assetType.get()

    asset_root_path = os.path.join(proj.assets_path, asset_type, asset_name[0].lower(), asset_name)

    file_path = cmds.file(q=True, sn=1).replace("\\", "/")
    file_name = file_path.split("/")[-1]

    if version is None:
        version = list(set(re.findall("v\d{3}.ma$", file_name)))[0].replace(".ma", "")

    # Update world_node to include the model attribute with the current version number

    # Check for stage attr, add if it doesn't exist
    if not hasattr(world_node, "build{}".format(stage)):
        cmds.addAttr(str(world_node), ln="build{}".format(stage), dt="string")

    # Set the stage attribute
    getattr(world_node, 'build{}'.format(stage)).set(version)

    logger.info("Asset world node build%s version set to: %s", stage, version)

    # Save file to publish folder
    publish_file_path = os.path.join(asset_root_path,
                                     "0{}_{}".format(str(STAGES.index(stage.lower()) + 1), stage.lower()),
                                     "publish",
                                     "{}_{}.ma".format(asset_name, stage.lower()))

    cmds.file(save=True, type="mayaAscii")

    if os.path.isfile(publish_file_path):
        os.remove(publish_file_path)

    if os.path.isfile(file_path):
        copyfile(file_path.replace("\\", "/"), publish_file_path)
    else:
        logger.error("file does not exist %s", file_path)
        return

    if os.path.isfile(publish_file_path):
        logger.info("Published %s file successfully", stage.lower())

    asset_data = {
        'asset_name': asset_name,
        'asset_type': asset_type
    }

    publish_asset_stage_json(asset_data, stage.lower(), version)

    # Stage specific publishes
    if stage.lower() == "build":
        publish_build_to_master(asset_data)
    elif stage.lower() == "lookdev":
        pm.select(cl=1)
        pm.select(world_node)
        export_shaders.export_shaders()

    function = r"F:\share\tools\tools_core\python\maya_core\pipeline\Asset\publish\update_world_node.py"

    arg = '{0} {1} {2} {3} {4}'.format(asset_name, asset_type, stage, version, proj.project_name)

    log_path = os.path.join(asset_root_path, '00_data', 'logs', "update_world_node_log.{}.txt".format(time.time()))
    f = open(log_path, "w")

    subprocess.call(['mayapy', function, arg], stdout=f, stderr=subprocess.STDOUT)
