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
from maya_core.asset_manager.asset import Asset

log = Logger()


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


class PMWidgetItem(QtWidgets.QTreeWidgetItem):

    def __init__(self, node, *args, **kwargs):
        super(PMWidgetItem, self).__init__(*args, **kwargs)
        self.pm_node = node


class TextureManagerUI(QtWidgets.QMainWindow):
    def __init__(self, parent=MWidgets.maya_main_window()):
        super(TextureManagerUI, self).__init__(parent)

        self.setWindowTitle("Texture Manager")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.setMinimumSize(1500 * .75, 900 * .75)

        self.asset = None
        self.objs = cmds.ls(sl=1)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

        self.refresh_tex()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.asset_root_lbl = QtWidgets.QLabel("Asset Root:  ")
        self.asset_root_le = QtWidgets.QLineEdit()

        file_browse_icon = QtGui.QIcon(':fileOpen.png')
        self.browse_btn = QtWidgets.QPushButton()
        self.browse_btn.setIcon(file_browse_icon)

        self.publish_tex_btn = QtWidgets.QPushButton("Publish Images")
        self.remap_tex_btn = QtWidgets.QPushButton("Remap Images")

        self.header_lbl = MWidgets.HeaderLabel("Texture Manager")

        self.refresh_btn = MWidgets.ImagePushButton(30, 30)
        self.refresh_btn.set_image("F:\\share\\tools\\shelf_icons\\refresh.png")
        self.refresh_btn.setFixedSize(30, 30)

        self.tex_tw = QtWidgets.QTreeWidget()
        # self.tex_tw.setHeaderHidden(True)

        self.show_errors_cb = QtWidgets.QCheckBox("Only show missing/empty")
        self.show_errors_cb.setChecked(0)

        header_item = QtWidgets.QTreeWidgetItem(["Shader / Texture", "File Path"])
        self.tex_tw.setHeaderItem(header_item)
        self.tex_tw.setAlternatingRowColors(True)

        self.stats_lbl = QtWidgets.QLabel()

    def create_layout(self):
        central_widget = QtWidgets.QWidget(self)
        m = 10
        central_widget.setContentsMargins(m, m, m, m)
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)

        header_layout = QtWidgets.QHBoxLayout()
        header_layout.addWidget(self.header_lbl)
        header_layout.addStretch()
        header_layout.addWidget(self.show_errors_cb)
        header_layout.addWidget(self.refresh_btn)

        asset_root_layout = QtWidgets.QHBoxLayout()
        asset_root_layout.addWidget(self.asset_root_lbl)
        asset_root_layout.addWidget(self.asset_root_le)
        asset_root_layout.addWidget(self.browse_btn)

        btns_layout = QtWidgets.QHBoxLayout()

        btns_layout.addWidget(self.stats_lbl)
        btns_layout.addStretch()
        btns_layout.addWidget(self.remap_tex_btn)
        btns_layout.addWidget(self.publish_tex_btn)

        main_layout.addLayout(header_layout)
        main_layout.addWidget(MWidgets.QHLine())
        main_layout.addLayout(asset_root_layout)
        main_layout.addWidget(self.tex_tw)
        main_layout.addLayout(btns_layout)

    def create_connections(self):
        self.publish_tex_btn.clicked.connect(self.publish_textures)
        self.remap_tex_btn.clicked.connect(self.set_paths)
        self.browse_btn.clicked.connect(self.browse_path)
        self.refresh_btn.clicked.connect(self.refresh_tex)

        self.tex_tw.itemSelectionChanged.connect(self.update_selection)
        self.show_errors_cb.stateChanged.connect(self.refresh_tex)

    def update_selection(self):
        try:
            item = self.tex_tw.selectedItems()[0]
            pm.select(item.pm_node)
        except Exception:
            pass

    def browse_path(self):
        library_path = "F:\\share\\assets\\libraries\\"

        asset_path = QtWidgets.QFileDialog.getExistingDirectory(self, 'asset Root', library_path)
        self.asset = Asset(path=asset_path)

        self.asset_root_le.setText(asset_path)

    def publish_textures(self):
        if not self.asset:
            return

        unique_tex_new_path = {}

        for mat, textures in self.mat_data.items():
            mat_node = pm.PyNode(mat)

            for tex in textures:
                src_path = tex.fileTextureName.get().replace("/", "\\")
                tex_name = src_path.split("\\")[-1]
                new_path = os.path.join(self.asset.textures_path, tex_name)

                unique_tex_new_path[tex] = (src_path, new_path)

        for tex, paths in unique_tex_new_path.items():
            try:
                copyfile(paths[0], paths[1])
                tex.fileTextureName.set(paths[1])
            except Exception as e:
                log.warning("Error copying file: " + str(e))
                pass

        self.close()

    def set_paths(self):
        if not self.asset:
            return

        unique_tex_new_path = {}

        for mat, textures in self.mat_data.items():
            mat_node = pm.PyNode(mat)

            for tex in textures:
                src_path = tex.fileTextureName.get().replace("/", "\\")
                tex_name = src_path.split("\\")[-1]
                new_path = os.path.join(self.asset.textures_path, tex_name)

                unique_tex_new_path[tex] = (src_path, new_path)

        for tex, paths in unique_tex_new_path.items():
            try:
                tex.fileTextureName.set(paths[1])
            except Exception as e:
                log.warning("Error copying file: " + str(e))
                pass

        self.refresh_tex()

    def refresh_tex(self):
        self.tex_tw.clear()

        self.mat_data = {}
        self.empty_textures = []
        self.missing_textures = []

        search = RecursiveNodeSearch()

        if not self.objs:
            self.objs = cmds.ls(sl=True)

        for obj in self.objs:
            cmds.hyperShade(shaderNetworksSelectMaterialNodes=1)
            material_selection = cmds.ls(sl=1)
            for mat in material_selection:
                connections = cmds.listConnections(mat)

                textures_tmp = []

                for c in connections:
                    nodes = search.search_nodes(c, "file")
                    textures_tmp.extend(nodes[1])

                textures = sorted(list(set(textures_tmp)))

                self.mat_data[mat] = textures

        for mat, textures in self.mat_data.items():
            mat_node = pm.PyNode(mat)

            mat_item = PMWidgetItem(mat_node)
            mat_item.setChildIndicatorPolicy(QtWidgets.QTreeWidgetItem.DontShowIndicatorWhenChildless)
            mat_item.setText(0, mat)

            tex_error = False
            mat_has_issue = False
            for tex in textures:
                tex_has_issue = False

                tex_item = PMWidgetItem(tex)
                tex_item.setText(0, str(tex))
                tex_item.setText(1, tex_item.pm_node.fileTextureName.get())

                if not os.path.isfile(tex_item.pm_node.fileTextureName.get()):
                    tex_has_issue = True
                    mat_has_issue = True
                    if tex_item.pm_node.fileTextureName.get() == "":
                        color = "yellow"
                        self.empty_textures.append(tex)
                    else:
                        color = "red"
                        tex_error = True
                        self.missing_textures.append(tex)

                    tex_item.setTextColor(0, QtGui.QColor(color))
                    tex_item.setTextColor(1, QtGui.QColor(color))
                    mat_item.setTextColor(0, QtGui.QColor(color))

                if self.show_errors_cb.isChecked() and tex_has_issue:
                    mat_item.addChild(tex_item)
                elif not self.show_errors_cb.isChecked():
                    mat_item.addChild(tex_item)

            if tex_error:
                mat_item.setTextColor(0, QtGui.QColor("red"))

            if self.show_errors_cb.isChecked() and not mat_has_issue:
                continue

            self.tex_tw.addTopLevelItem(mat_item)

        self.tex_tw.resizeColumnToContents(0)
        self.tex_tw.resizeColumnToContents(1)

        message = "Empty Textures: {0}, Missing Textures: {1}".format(len(list(set(self.empty_textures))),
                                                                      len(list(set(self.missing_textures))))

        self.stats_lbl.setText(message)

        cmds.select(self.objs)


def main():
    try:
        dialog.close()
        dialog.deleteLater()
    except:
        pass

    dialog = TextureManagerUI()
    dialog.show()


if __name__ == "__main__":
    main()
