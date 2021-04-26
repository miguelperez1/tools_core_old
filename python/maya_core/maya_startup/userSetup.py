import maya.cmds as cmds

import maya_core
from maya_core.common_tools import logger

log = logger.Logger()


def set_render_settings():
    cmds.setAttr("vraySettings.aspectLock", 0)

    cmds.setAttr("vraySettings.width", 1920)
    cmds.setAttr("vraySettings.height", 804)

    cmds.setAttr("vraySettings.aspectRatio", 2.388)
    cmds.setAttr("vraySettings.pixelAspect", 1.000)
    cmds.setAttr("vraySettings.clearRVOn", 1)


def startup_maya():
    log.result("loaded tools_core-" + maya_core.version)

    cmds.setAttr("defaultRenderGlobals.currentRenderer", "vray", type="string")
    log.result("Set V-Ray as current renderer")

    cmds.objExists("vraySettings")


cmds.evalDeferred(startup_maya, lp=1)
cmds.evalDeferred(set_render_settings, lp=1)
