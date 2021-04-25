import maya.cmds as cmds
import pymel.core as pm


def create_cc_node(source_node):
    # Store original outcolor connections
    out_connections = pm.listConnections(source_node + ".outColor")

    # Create CC Node
    cc_node = pm.shadingNode('colorCorrect', n=source_node + "_CC", asUtility=True)

    # Connect file to cc
    pm.connectAttr(source_node + ".outColor", cc_node + ".inColor")

    # Connect cc to original connections
    for connection in out_connections:
        out_attr = connection[-1]

        pm.connectAttr(cc_node+".outColor", out_attr)
