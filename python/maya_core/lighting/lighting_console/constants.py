import maya.cmds as cmds
import pymel.core as pm

from collections import OrderedDict

SCALE = 1
RES_X = 2560 * SCALE
RES_Y = 1440 * SCALE
GLOBAL_SPACING = 7

ICONS = {
    "VRayLightRectShape": "C:\\Program Files\\Autodesk\\Maya2020\\vray\\icons\\shelf_LightRect_200.png",
    "VRayLightSphereShape": "C:\\Program Files\\Autodesk\\Maya2020\\vray\\icons\\shelf_LightSphere_200.png",
    "VRayLightDomeShape": "C:\\Program Files\\Autodesk\\Maya2020\\vray\\icons\\shelf_LightDome_200.png",
    "directionalLight": ":/directionallight.png",
    "connection_in": ":/hsUpStreamCon.png",
    "group": "F:\\share\\tools\\shelf_icons\\group.png"
}


class RecursiveNodeSearch(object):
    def _traverse(self, node, children):

        connections = []

        for c in pm.listRelatives(node, c=True):
            connections.append(str(c))

        for child in connections:
            children[child] = {}

    def get_nodes(self, node, children):
        self._traverse(node, children)

        for child in children:
            self._traverse(child, children[child])

    def search_nodes(self, node):
        children = {}
        self.get_nodes(node, children)

        return children
