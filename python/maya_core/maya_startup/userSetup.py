import maya.cmds as cmds
import maya.mel as mel

import maya_core
from maya_core.common_tools import logger
from maya_core import maya_startup

log = logger.Logger()

version = "1.0.2"


def set_render_settings():
    cmds.setAttr("defaultRenderGlobals.currentRenderer", "vray", type="string")
    log.result("Set V-Ray as current renderer")

    mel.eval("vrayCreateVRaySettingsNode();")

    cmds.setAttr("vraySettings.aspectLock", 0)
    cmds.setAttr("vraySettings.width", 1920)
    cmds.setAttr("vraySettings.height", 696)
    cmds.setAttr("vraySettings.aspectRatio", 1920 / 696)
    cmds.setAttr("vraySettings.pixelAspect", 1)
    cmds.setAttr("vraySettings.imageFormatStr", "exr", type="string")


def startup_maya():
    log.result("startup version-" + version)
    log.result("loaded tools_core-" + maya_core.version)
    set_render_settings()


def main():
    cmds.evalDeferred(startup_maya, lp=1)


if __name__ == "__main__" or __name__ == "maya_core.maya_startup.userSetup":
    main()
