import maya.cmds as cmds
import maya.mel as mel

import maya_core
from maya_core.common_tools import logger

log = logger.Logger()


def set_render_settings():
    cmds.setAttr("defaultResolution.width", 1920)
    cmds.setAttr("defaultResolution.height", 804)
    cmds.setAttr("defaultResolution.lockDeviceAspectRatio", 0)
    cmds.setAttr("defaultResolution.deviceAspectRatio", (1920 / 804))
    cmds.setAttr("defaultResolution.pixelAspect", 1.0)

    cmds.setAttr("defaultRenderGlobals.currentRenderer", "vray", type="string")
    log.result("Set V-Ray as current renderer")

    mel.eval("vrayCreateVRaySettingsNode();")

    cmds.setAttr("vraySettings.aspectLock", 0)
    cmds.setAttr("vraySettings.width", 1920)
    cmds.setAttr("vraySettings.height", 804)
    cmds.setAttr("vraySettings.aspectRatio", 1920/804)
    cmds.setAttr("vraySettings.pixelAspect", 1)


def startup_maya():
    log.result("loaded tools_core-" + maya_core.version)
    set_render_settings()


def main():
    cmds.evalDeferred(startup_maya, lp=1)


if __name__ == "__main__" or __name__ == "maya_core.maya_startup.userSetup":
    main()
