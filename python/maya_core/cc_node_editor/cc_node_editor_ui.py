from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import maya.cmds as cmds

import os
import sys
import subprocess


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


def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class CCNodeEditor(QtWidgets.QDialog):
    """
    Dialog used to demonstrates many of the standard dialogs available in Qt
    """

    def __init__(self, parent=maya_main_window()):
        super(CCNodeEditor, self).__init__(parent)

        self.setWindowTitle("CC Node Editor")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.setFixedSize(500, 500)

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.go_btn = QtWidgets.QPushButton("Find CC Nodes")

        self.cc_nodes_tw = QtWidgets.QTreeWidget()

        self.cc_nodes_tw.setHeaderHidden(True)
        self.cc_nodes_tw.setAlternatingRowColors(True)

        self.current_obj = QtWidgets.QLabel("Current Selection: ")

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.addWidget(self.go_btn)
        main_layout.addWidget(self.current_obj)
        main_layout.addWidget(self.cc_nodes_tw)

    def create_connections(self):
        self.go_btn.clicked.connect(self.create_cc_widgets)
        self.cc_nodes_tw.currentItemChanged.connect(self.cc_nodes_tw_changed_callback)

    def cc_nodes_tw_changed_callback(self):
        cmds.select(self.cc_nodes_tw.currentItem().text(0))

    def create_cc_widgets(self):
        self.cc_nodes_tw.clear()

        self.find_cc_nodes()

        for n in self.cc_nodes:
            cc_node_item = QtWidgets.QTreeWidgetItem()
            cc_node_item.setText(0, n)

            self.cc_nodes_tw.addTopLevelItem(cc_node_item)

        self.current_obj.setText("Current Selection: {}".format(", ".join(self.objs)))

    def find_cc_nodes(self):
        self.cc_nodes = []
        self.objs = []

        search = RecursiveNodeSearch()

        for obj in cmds.ls(sl=True):
            self.objs.append(obj)
            cmds.hyperShade(shaderNetworksSelectMaterialNodes=1)
            material_selection = cmds.ls(sl=1)

            for mat in material_selection:
                connections = cmds.listConnections(mat)

                cc_nodes_tmp = []

                for c in connections:
                    nodes = search.search_nodes(c)

                    for n in nodes:
                        if cmds.nodeType(n) == "colorCorrect":
                            cc_nodes_tmp.append(n)

                cc_nodes = list(set(cc_nodes_tmp))

                for node in cc_nodes:
                    self.cc_nodes.append(node)


if __name__ == "__main__" or __name__ == "maya_core.cc_node_editor.cc_node_editor_ui":
    try:
        dialog.close()
        dialog.deleteLater()
    except:
        pass

    dialog = CCNodeEditor()
    dialog.show()
