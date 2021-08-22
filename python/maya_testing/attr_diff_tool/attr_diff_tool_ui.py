from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import pymel.core as pm

import json
import re


class AttrDiffToolUI(QtWidgets.QMainWindow):
    def __init__(self, parent=[i for i in QtWidgets.QApplication.topLevelWidgets() if i.objectName() == 'MayaWindow'][0]):
        super(AttrDiffToolUI, self).__init__(parent)

        self.setWindowTitle("Attr Diff Tool")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.setObjectName("AttrDiffToolUI")

        self.setMinimumWidth(500)

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.file_lbl = QtWidgets.QLabel("Save to")
        self.file_le = QtWidgets.QLineEdit()
        self.file_btn = QtWidgets.QPushButton()

        file_browse_icon = QtGui.QIcon(':fileOpen.png')
        self.file_btn.setIcon(file_browse_icon)

        self.node_lbl = QtWidgets.QLabel("Node ")
        self.node_le = QtWidgets.QLineEdit()
        self.node_selected_btn = QtWidgets.QPushButton("Use Selected")

        self.node_children_cb = QtWidgets.QCheckBox("Descendants")

        self.run_diff_btn = QtWidgets.QPushButton("Run Diff")
        self.store_attr_btn = QtWidgets.QPushButton("Store Attrs")

    def create_layout(self):
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)

        file_layout = QtWidgets.QHBoxLayout()
        file_layout.addWidget(self.file_lbl)
        file_layout.addWidget(self.file_le)
        file_layout.addWidget(self.file_btn)

        main_layout.addLayout(file_layout)

        options_layout = QtWidgets.QHBoxLayout()
        options_layout.addWidget(self.node_lbl)
        options_layout.addWidget(self.node_le)
        options_layout.addWidget(self.node_selected_btn)
        options_layout.addWidget(self.node_children_cb)

        main_layout.addLayout(options_layout)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.store_attr_btn)
        btn_layout.addWidget(self.run_diff_btn)

        main_layout.addLayout(btn_layout)

    def create_connections(self):
        self.node_selected_btn.clicked.connect(self.use_selected_cb_callback)

    def store_attrs(self):
        data = {}

        nodes = []

        nodes.extend(self.node_le.text().split(","))

        if self.node_children_cb.isChecked():
            for node in self.node_le.text().split(","):
                nodes.extend(pm.listRelatives(node, ad=1))

        for node in nodes:
            for attr in pm.listAttr(node):
                try:
                    key = "{}.{}".format(str(node), str(attr))
                    value = cmds.getAttr(key)

                    if not (isinstance(value, float) or isinstance(value, int)):
                        continue
                    data[key] = value
                except:
                    pass

        with open(self.file_le.text(), "w") as f:
            json.dump(data, f, indent=4)

    def use_selected_cb_callback(self):
        nodes = ",".join([str(n) for n in pm.ls(sl=1)])
        self.node_le.setText(nodes)


def main():
    try:
        cmds.deleteUI("AttrDiffToolUI")
    except Exception:
        pass

    dialog = AttrDiffToolUI()
    dialog.show()


if __name__ == "__main__":
    main()
