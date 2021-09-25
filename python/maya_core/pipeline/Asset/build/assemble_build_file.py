import os

import pymel.core as pm
import maya.cmds as cmds

from maya_core.pipeline.project import maya_project

def assemble_build_file(asset_name, asset_type):
    project = maya_project.get_current_project()

    asset_root_path = os.path.join(project.assets_path, asset_type, asset_name[0].lower(), asset_name)

    if asset_type == "set":
        # Use the dress file
        pass
    elif asset_type == "character":
        # Use the rig file
        pass

    # Grab the lighting file

    # Do fancy stuff to merge the two

    # Save file