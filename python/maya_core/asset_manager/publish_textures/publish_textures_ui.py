from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import os
from collections import defaultdict
from shutil import copyfile

import maya.cmds as cmds
import pymel.core as pm

from pyqt_commons import MWidgets
from maya_core.common_tools.logger import Logger

log = Logger()


class RecursiveNodeSearch(object):
    def _traverse(self, node, children):

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
            self._traverse(child, children[child])

    def search_nodes(self, node):
        children = {}
        self.get_nodes(node, children)

        return children


class PublishTexturesUI(QtWidgets.QMainWindow):
    def __init__(self, parent=MWidgets.maya_main_window()):
        super(PublishTexturesUI, self).__init__(parent)

        self.setWindowTitle("Publish Textures")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.setMinimumSize(500, 100)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.asset_root_lbl = QtWidgets.QLabel("Asset root:  ")
        self.asset_root_le = QtWidgets.QLineEdit()

        file_browse_icon = QtGui.QIcon(':fileOpen.png')
        self.browse_btn = QtWidgets.QPushButton()
        self.browse_btn.setIcon(file_browse_icon)

        self.publish_tex_btn = QtWidgets.QPushButton("Publish")
        self.remap_tex_btn = QtWidgets.QPushButton("Remap Images")

    def create_layout(self):
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)

        search_layout = QtWidgets.QHBoxLayout()
        search_layout.addWidget(self.asset_root_lbl)
        search_layout.addWidget(self.asset_root_le)
        search_layout.addWidget(self.browse_btn)

        main_layout.addLayout(search_layout)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.remap_tex_btn)
        btn_layout.addWidget(self.publish_tex_btn)

        main_layout.addLayout(btn_layout)

    def create_menu(self):
        self.menu_bar = QtWidgets.QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        file_menu = QtWidgets.QMenu("File", self)
        edit_menu = QtWidgets.QMenu("Edit", self)
        tools_menu = QtWidgets.QMenu("Tools", self)
        help_menu = QtWidgets.QMenu("Help", self)

        self.menu_bar.addMenu(file_menu)
        self.menu_bar.addMenu(edit_menu)
        self.menu_bar.addMenu(tools_menu)
        self.menu_bar.addMenu(help_menu)

    def create_connections(self):
        self.publish_tex_btn.clicked.connect(self.publish_textures)
        self.remap_tex_btn.clicked.connect(self.set_paths)
        self.browse_btn.clicked.connect(self.browse_path)

    def browse_path(self):
        library_path = "F:\\share\\assets\\libraries\\"

        asset_path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Asset Root', library_path)

        self.asset_root_le.setText(asset_path)

    def publish_textures(self):
        asset_root_path = self.asset_root_le.text()

        mat_data = defaultdict(list)

        search = RecursiveNodeSearch()

        for obj in cmds.ls(sl=True):
            cmds.hyperShade(shaderNetworksSelectMaterialNodes=1)
            material_selection = cmds.ls(sl=1)
            for mat in material_selection:
                mat_tex_dst = asset_root_path + "\\textures\\" + mat
                if not os.path.isdir(mat_tex_dst):
                    os.mkdir(mat_tex_dst)

                connections = cmds.listConnections(mat)

                textures_tmp = []

                for c in connections:
                    nodes = search.search_nodes(c)
                    for n in nodes:
                        if cmds.nodeType(n) == "file":
                            textures_tmp.append(n)

                textures = list(set(textures_tmp))

                mat_data[mat_tex_dst].append(textures)

        if len(mat_data.keys()) > 0:
            for mat_tex_src, texture_lists in mat_data.items():
                for textures in texture_lists:
                    for tex in textures:
                        tex_src_path = cmds.getAttr('{}.fileTextureName'.format(tex))

                        tex_name = tex_src_path.split('/')[-1]

                        tex_dst_path = (mat_tex_src + "\\{}".format(tex_name))

                        log.info("copying {0} to {1}".format(tex_src_path, tex_dst_path))

                        try:
                            copyfile(tex_src_path, tex_dst_path)
                            log.info("copied successfully")
                        except Exception as e:
                            log.warning("copy failed, skipping: {}".format(e))

                        cmds.setAttr("{}.fileTextureName".format(tex), tex_dst_path, type="string")

        self.close()

    def set_paths(self):
        asset_root_path = self.asset_root_le.text()

        mat_data = defaultdict(list)

        search = RecursiveNodeSearch()

        for obj in cmds.ls(sl=True):
            cmds.hyperShade(shaderNetworksSelectMaterialNodes=1)
            material_selection = cmds.ls(sl=1)
            for mat in material_selection:
                mat_tex_dst = asset_root_path + "\\textures\\" + mat

                connections = cmds.listConnections(mat)

                textures_tmp = []

                for c in connections:
                    nodes = search.search_nodes(c)
                    for n in nodes:
                        if cmds.nodeType(n) == "file":
                            textures_tmp.append(n)

                textures = list(set(textures_tmp))

                mat_data[mat_tex_dst].append(textures)

        if len(mat_data.keys()) > 0:
            for mat_tex_src, texture_lists in mat_data.items():
                for textures in texture_lists:
                    for tex in textures:
                        tex_src_path = cmds.getAttr('{}.fileTextureName'.format(tex))

                        tex_name = tex_src_path.split('/')[-1]

                        tex_dst_path = (mat_tex_src + "\\{}".format(tex_name))

                        if os.path.isfile(tex_dst_path):
                            cmds.setAttr("{}.fileTextureName".format(tex), tex_dst_path, type="string")
                            log.result("Repathed\n{0}\n{1}".format(tex_src_path, tex_dst_path))


def main():
    try:
        dialog.close()
        dialog.deleteLater()
    except:
        pass

    dialog = PublishTexturesUI()
    dialog.show()


if __name__ == "__main__":
    main()
