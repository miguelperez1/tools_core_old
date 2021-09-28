import os
import logging

import pymel.core as pm
import maya.cmds as cmds

from maya_core.pipeline.project import maya_project
from maya_core.modeling.normalize_scale import normalize_scale

GLOBAL_CTRLS_PATH = os.path.join(maya_project.get_project("studio").assets_path, "rig", "g", "GlobalCtrls",
                                 "GlobalCtrls.ma")

logger = logging.getLogger(__name__)
logger.setLevel(10)


def apply_global_ctrls(node=None):
    if node is None:
        selected_nodes = pm.ls(sl=1)

        if not selected_nodes:
            logger.error("No node selected")
            return
        else:
            node = selected_nodes[0]

    if not hasattr(node, "assetName"):
        logger.error("%s is not an asset world node", str(node))
        return
    elif pm.objExists("GlobalCtrls"):
        if len(pm.listRelatives("GlobalCtrls", ap=1)) == 0:
            logger.error("GlobalCtrls is already top level in scene")
            return

    logger.info("Applying global controls to %s", str(node))

    asset_name = node.assetName.get()

    # import ctrls
    cmds.file(GLOBAL_CTRLS_PATH, i=True, ignoreVersion=True, force=True)

    # parent under ctrls group
    controls_node = None
    for c in (node.listRelatives(c=1)):
        if "Rig" in str(c):
            for gc in c.listRelatives(c=1):
                if "Controls" in str(gc):
                    controls_node = gc

    if controls_node is None:
        logger.error("Could not find controls group")
        return

    pm.parent("GlobalCtrls", controls_node)

    # Scale GlobalCtrls to the larger bbox

    # find geo constrain group
    constrain_node = None
    for c in (node.listRelatives(c=1)):
        if "Geometry" in str(c):
            for gc in c.listRelatives(c=1):
                if "HiRes" in str(gc):
                    for ggc in gc.listRelatives(c=1):
                        if "Constrain" in str(ggc):
                            constrain_node = ggc

    if constrain_node is None:
        logger.error("Could not find geometry constrain group")
        return

    # scale controls to constrain bbox
    longest_axis = normalize_scale.get_longest_axis(constrain_node, skip_axis='y')

    normalize_scale.normalize_scale(longest_axis[0], pm.PyNode("GlobalCtrls"), axis=longest_axis[1])

    # constrain controls
    constrain_ctrl = pm.PyNode("global_03_ctrl")

    pm.parentConstraint(constrain_ctrl, constrain_node, mo=1)
    pm.scaleConstraint(constrain_ctrl, constrain_node, mo=1)
