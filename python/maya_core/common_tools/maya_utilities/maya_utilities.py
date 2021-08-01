import pymel.core as pm
import maya.cmds as cmds


def filter_connected_nodes(node, node_type=None):
    connected_nodes = []

    if node_type:
        connections = cmds.ls(*cmds.listHistory(str(node)), type=node_type)
        if connections:
            connected_nodes.extend([pm.PyNode(n) for n in connections])
    else:
        connections = cmds.ls(*cmds.listHistory(str(node)))
        if connections:
            connected_nodes.extend([pm.PyNode(n) for n in connections])

    return connected_nodes


def get_materials_from_selection():
    materials = []

    for obj in cmds.ls(sl=1, dag=1, s=1):
        sgs = pm.listConnections(obj, type="shadingEngine")
        for sg in sgs:
            mats = pm.listConnections(sg.surfaceShader)
            if pm.sets(sg, q=1):
                if mats:
                    materials.extend(mats)

    return materials


def get_materials_from_node(nodes=None):
    materials = []

    for obj in nodes:
        sgs = pm.listConnections(obj, type="shadingEngine")
        for sg in sgs:
            mats = pm.listConnections(sg.surfaceShader)
            if pm.sets(sg, q=1):
                if mats:
                    materials.extend(mats)

    return materials


def get_all_materials():
    materials = []

    for sg in pm.ls(type="shadingEngine"):
        mats = pm.listConnections(sg.surfaceShader)
        if pm.sets(sg, q=1):
            if mats:
                materials.extend(mats)

    return materials
