import os

from maya_core.pipeline.project import maya_project

def create_asset(asset_name, asset_type):
    current_project = maya_project.get_current_project()

