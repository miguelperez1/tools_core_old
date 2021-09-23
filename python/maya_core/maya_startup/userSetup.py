import os
import sys
from shutil import copyfile

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm

import maya_core

from maya_core.pipeline.project import maya_project
from maya_core.maya_menu import maya_menu


def set_default_workspace():
    maya_project.set_maya_project(maya_project.default_project_root)


def set_render_settings():
    cmds.setAttr("defaultRenderGlobals.currentRenderer", "vray", type="string")

    mel.eval("vrayCreateVRaySettingsNode();")

    cmds.setAttr("vraySettings.aspectLock", 0)
    cmds.setAttr("vraySettings.width", 1920)
    cmds.setAttr("vraySettings.height", 804)
    cmds.setAttr("vraySettings.aspectRatio", 1920 / 804)
    cmds.setAttr("vraySettings.pixelAspect", 1)
    cmds.setAttr("vraySettings.rgbColorSpace", 2)
    cmds.setAttr("vraySettings.imageFormatStr", "exr (multichannel)", type="string")
    cmds.setAttr("vraySettings.fileNamePrefix", "<Scene>.<Layer>", type="string")

    mel.eval("updateRendererUI")

    if cmds.objExists("persp"):
        camera = pm.PyNode("persp")
        camera.farClipPlane.set(100000)


def startup_maya():
    mel.eval("loadPlugin vrayformaya")
    set_render_settings()
    set_default_workspace()
    maya_menu.create_studio_menu()


def main():
    sys.path.append(r"C:\Python27\Lib\site-packages")
    cmds.evalDeferred(startup_maya, lp=1)


def copy_user_setup():
    dst_file = r"C:\Users\Miguel\Documents\maya\scripts\userSetup.py"
    src_file = r"F:\share\tools\tools_core\python\maya_core\maya_startup\userSetup.py"

    if os.path.isfile(dst_file):
        os.remove(dst_file)

    copyfile(src_file, dst_file)

    if os.path.isfile(dst_file):
        print("Copied userSetup.py")


if __name__ == "__main__":
    copy_user_setup()
    try:
        main()
    except:
        pass
