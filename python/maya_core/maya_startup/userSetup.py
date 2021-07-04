import os
import sys
from shutil import copyfile

import maya.cmds as cmds
import maya.mel as mel

import maya_core

# from maya_core.common_tools import logger
# from maya_core import maya_startup
from maya_core.pipeline.project import maya_project

# log = logger.Logger()

version = "1.0.2"


def set_default_workspace():
    maya_project.set_maya_project(maya_project.default_project_root)


def set_render_settings():
    cmds.setAttr("defaultRenderGlobals.currentRenderer", "vray", type="string")

    mel.eval("vrayCreateVRaySettingsNode();")

    cmds.setAttr("vraySettings.aspectLock", 0)
    cmds.setAttr("vraySettings.width", 1920)
    cmds.setAttr("vraySettings.height", 696)
    cmds.setAttr("vraySettings.aspectRatio", 1920 / 696)
    cmds.setAttr("vraySettings.pixelAspect", 1)
    cmds.setAttr("vraySettings.imageFormatStr", "exr", type="string")


def startup_maya():
    # log.result("startup version-" + version)
    # log.result("loaded tools_core-" + maya_core.version)
    mel.eval("loadPlugin vrayformaya")
    set_render_settings()
    set_default_workspace()


def main():
    sys.path.append(r"C:\Python27\Lib\site-packages")
    cmds.evalDeferred(startup_maya, lp=1)


def copy_user_setup():
    dst_file = r"C:\Users\Miguel\Documents\maya\scripts\userSetup.py"
    src_file = r"F:\share\tools\tools_core\python\maya_core\maya_startup\userSetup.py"

    if os.path.isfile(dst_file):
        os.remove(dst_file)

    copyfile(src_file, dst_file)


if __name__ == "__main__":
    main()
