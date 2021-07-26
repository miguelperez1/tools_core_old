import maya.OpenMaya as om
import maya.OpenMayaMPx as ommpx

import maya.cmds as cmds


class BasicDeformerNode(ommpx.MPxDeformerNode):
    TYPE_NAME = "basicdeformernode"
    TYPE_ID = om.MTypeId(0x0007F7FC)

    def __init__(self):
        super(BasicDeformerNode, self).__init__()

    @classmethod
    def creator(cls):
        return BasicDeformerNode()

    @classmethod
    def initialize(cls):
        pass


def initializePlugin(plugin):
    vendor = "Chris Zurbrigg"
    version = "1.0.0"

    plugin_fn = ommpx.MFnPlugin(plugin, vendor, version)

    try:
        plugin_fn.registerNode(BasicDeformerNode.TYPE_NAME,
                               BasicDeformerNode.TYPE_ID,
                               BasicDeformerNode.creator,
                               BasicDeformerNode.initialize,
                               ommpx.MPxNode.kDeformerNode)
    except:
        om.MGlobal.displayError("Failed to register node: {0}".format(BasicDeformerNode.TYPE_NAME))

    cmds.makePaintable(BasicDeformerNode.TYPE_NAME, 'weights', attrType='multiFloat', shapeMode='deformer')


def uninitializePlugin(plugin):
    plugin_fn = ommpx.MFnPlugin(plugin)

    try:
        plugin_fn.deregisterNode(BasicDeformerNode.TYPE_ID)
    except:
        om.MGlobal.displayError("Failed to deregister node: {0}".format(BasicDeformerNode.TYPE_NAME))
