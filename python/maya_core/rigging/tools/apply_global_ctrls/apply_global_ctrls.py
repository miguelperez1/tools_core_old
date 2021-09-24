import os
import logging

import pymel.core as pm
import maya.cmds as cmds

from maya_core.pipeline.project import maya_project

reload(maya_project)

GLOBAL_CTRLS_PATH = os.path.join(maya_project.get_project("studio").assets_path, "rig", "g", "GlobalCtrls",
                                 "GlobalCtrls.ma")

logger = logging.getLogger(__name__)
logger.setLevel(10)


def apply_global_ctrls(node=None):
    if node is None:
        node = pm.ls(sl=1)[0]

    if node is None:
        logger.error("No node selected")
        return

    if not hasattr(node, "assetName"):
        logger.error("%s is not an asset world node", str(node))
        return

    elif pm.objExists("GlobalCtrls"):
        if len(pm.listRelatives("GlobalCtrls", ap=1)) == 0:
            logger.error("GlobalCtrls is already top level in scene")
            return

    asset_name = node.assetName.get()

    # import ctrls
    cmds.file(GLOBAL_CTRLS_PATH, i=True, ignoreVersion=True, force=True)

    # parent under ctrls group
    pm.parent("GlobalCtrls", "{}|Controls".format(asset_name))

    # constrain to geo constrain group
    constrain_ctrl = pm.PyNode("global_03_ctrl")
    constrain_grp = pm.PyNode("{}|Geometry|Constrain".format(asset_name))

    pm.parentConstraint(constrain_ctrl, constrain_grp, mo=1)
    pm.scaleConstraint(constrain_ctrl, constrain_grp, mo=1)
