import os
import sys
import json
from shutil import copyfile
from maya_core.asset_manager.asset import Asset
import shutil

import maya.standalone

maya.standalone.initialize()

import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel

from maya_core import material_builder
from maya_core.asset_manager import texture_manager

from maya_core.common_tools import logger

log = logger.Logger()
log.status = True


class RecursiveNodeSearch(object):
    def __init__(self):
        self.filtered_nodes = []

    def _traverse(self, node, children):
        try:
            n = pm.PyNode(node)
            if n.nodeType() == self.node_type:
                self.filtered_nodes.append(n)
        except Exception:
            pass

        connections = cmds.listConnections(
            node,
            source=True,
            destination=False,
            skipConversionNodes=True) or {}

        for child in connections:
            children[child] = {}

    def get_nodes(self, node, children):
        self._traverse(node, children)

        for child in children:
            try:
                n = pm.PyNode(child)
                if n.nodeType() == self.node_type:
                    self.filtered_nodes.append(n)
            except Exception:
                pass

            self._traverse(child, children[child])

    def search_nodes(self, node, nodeType=None):
        self.node_type = nodeType
        children = {}
        self.get_nodes(node, children)

        return (children, self.filtered_nodes)


def build_maya(asset_data):
    asset = Asset(asset_data["name"], asset_data["type"])

    log.debug("Staring build_maya process")

    # Rename File

    cmds.file(rename=asset.maya_file_path)

    # Build Maya File
    #   Import Mesh
    if asset_data["type"] == "model":
        source_mesh = asset_data["mesh"].replace("/", "\\")

        log.debug("Importing {}".format(source_mesh))

        cmds.file(source_mesh, i=True)

        cmds.select(cmds.listRelatives(cmds.ls(geometry=True), p=True, path=True), r=True)

        model = cmds.ls(sl=1)[0]

        # Copy Mesh
        dst_mesh = os.path.join(asset.mesh_dir, source_mesh.split("\\")[-1])

        log.debug("Copying mesh")

        copyfile(source_mesh, dst_mesh)

        if os.path.isfile(dst_mesh):
            log.debug("Copied {}".format(dst_mesh))

    # Create Material
    # TODO Publish textures
    log.debug("Creating Material")

    material = None

    if asset_data["material"]["mat_type"] == "VRayMtl":
        material = material_builder.build_vraymtl(asset_data["material"])

    elif asset_data["material"]["mat_type"] == "VRayMtl2Sided":
        face_material = material_builder.build_vraymtl(asset_data["material"])
        material = material_builder.build_vray2sidedmtl(asset_data["material"]["name"], face_material, face_material)

    log.debug("Created {}".format(material))

    if asset_data["type"] == "model":
        if material:
            log.debug("Assigning {0} to {1}".format(material[-1], str(model)))
            cmds.sets(model, e=True, forceElement=material[-1])

    search = RecursiveNodeSearch()

    connections = cmds.listConnections(material[0])
    textures_tmp = []

    for c in connections:
        nodes = search.search_nodes(c, "file")
        textures_tmp.extend(nodes[1])

    textures = sorted(list(set(textures_tmp)))

    mat_data = {
        material[0]: textures
    }

    texture_manager.publish_textures(asset, mat_data)

    pm.rename(model, asset.name)

    log.debug("Saving maya file...")

    cmds.file(save=True, type="mayaAscii")

    if os.path.isfile(asset.maya_file_path):
        log.debug("Maya Built Successfully")

    # TODO Create Proxy
    if not asset_data["has_proxy"]:
        return

    proxy_path = asset.proxy_dir
    proxy_maya_path = proxy_path + "\\{0}_vrayproxy.ma".format(asset.name)

    pm.select(asset.name)

    cmds.select(clear=True)
    pm.select(asset.name)

    # export proxy
    cmds.vrayCreateProxy(exportType=1, previewFaces=17500, dir=proxy_path, fname=asset.name + ".vrmesh",
                         overwrite=True,
                         previewType="clustering", makeBackup=True, ignoreHiddenObjects=False, vertexColorsOn=True,
                         exportHierarchy=True, includeTransformation=True)

    # deslect everything
    cmds.select(clear=True)

    # create vray_proxy nodes
    vrmesh = asset.name + "_vrmesh"
    vraymeshmtl = vrmesh + "_vraymeshmtl"
    vrproxy_path = proxy_path + "\\{}.vrmesh".format(asset.name)

    cmds.vrayCreateProxy(createProxyNode=True, node=vrmesh, existing=True,
                         dir=vrproxy_path, geomToLoad=3, newProxyNode=False)

    # assign shader

    cmds.connectAttr("{}.outColor".format(material[0]), "{}.shaders[0]".format(vraymeshmtl))

    # select vray_proxy
    cmds.select(clear=True)

    # save selection as new maya file
    pm.select(vrmesh, r=1)
    pm.exportSelected(proxy_maya_path, type="mayaAscii", channels=True, force=True)


if __name__ == '__main__':
    mel.eval('loadPlugin vrayformaya')
    mel.eval('loadPlugin fbxmaya')

    json_file = open(sys.argv[1], "r")
    asset_data = json.load(json_file)
    json_file.close()

    build_maya(asset_data)
