import os
import re
import subprocess
from shutil import copyfile
from collections import OrderedDict, defaultdict

import maya.cmds as cmds
import pymel.core as pm

from maya_core.common_tools.logger import Logger

log = Logger()
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


def get_mat_data(objs):
    mat_data = {}

    search = RecursiveNodeSearch()

    for obj in objs:
        cmds.hyperShade(shaderNetworksSelectMaterialNodes=1)
        material_selection = cmds.ls(sl=1)
        for mat in material_selection:
            connections = cmds.listConnections(mat)

            textures_tmp = []

            for c in connections:
                nodes = search.search_nodes(c, "file")
                textures_tmp.extend(nodes[1])

            textures = sorted(list(set(textures_tmp)))

            mat_data[mat] = textures

    return mat_data


def publish_textures(asset, mat_data):
    if not asset:
        return

    unique_tex_new_path = {}

    for mat, textures in mat_data.items():
        mat_node = pm.PyNode(mat)

        for tex in textures:
            src_path = tex.fileTextureName.get().replace("/", "\\")
            tex_name = src_path.split("\\")[-1]
            new_path = os.path.join(asset.textures_dir, tex_name)

            unique_tex_new_path[tex] = (src_path, new_path)

    for tex, paths in unique_tex_new_path.items():
        try:
            copyfile(paths[0], paths[1])
            tex.fileTextureName.set(paths[1])
        except Exception as e:
            log.warning("Error copying file: " + str(e))
            pass
