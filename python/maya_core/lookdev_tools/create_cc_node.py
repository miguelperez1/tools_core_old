import maya.cmds as cmds
import pymel.core as pm


def create_cc_node(source_node):
    # Store original outcolor connections
    out_connections = pm.listConnections(source_node, connections=True, plugs=True)

    # Create CC Node
    cc_node = pm.shadingNode('colorCorrect', n=source_node + "_CC", asUtility=True)

    # Connect file to cc
    pm.connectAttr(source_node + ".outColor", cc_node + ".inColor")

    # Connect gamma attributes
    pm.connectAttr(cc_node + ".colGammaX", cc_node + ".colGammaY")
    pm.connectAttr(cc_node + ".colGammaX", cc_node + ".colGammaZ")

    # Connect cc to original connections
    for connection_pair in out_connections:
        out_attr = connection_pair[0].split(".")[-1]
        if out_attr.startswith("outColor") or out_attr == "outAlpha":
            source_connection = connection_pair[0].split(".")[-1]
            target_connection = connection_pair[-1]
            pm.connectAttr(cc_node + "." + source_connection, target_connection, f=True)


def main():
    selection = pm.ls(sl=True, typ="file")

    for node in selection:
        create_cc_node(node)
