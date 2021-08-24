from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import pymel.core as pm

from pyqt_commons import MWidgets
from maya_core.lookdev.material_builder_ui import material_builder_ui
from maya_core.lookdev.material_utils import material_utils
from maya_core.lookdev.cc_node_editor import cc_node_editor_ui

reload(material_utils)


class LookdevToolkitUI(QtWidgets.QMainWindow):
    def __init__(self, parent=MWidgets.maya_main_window()):
        super(LookdevToolkitUI, self).__init__(parent)

        self.setWindowTitle("Lookdev Toolkit")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.setObjectName("LookdevToolkitUI")
        self.setMinimumWidth(400)

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.material_builder_btn = QtWidgets.QPushButton("Material Builder")
        self.create_cc_btn = QtWidgets.QPushButton("Create Color Correct")
        self.create_texture_btn = QtWidgets.QPushButton("Create Texture")
        self.create_ptex_btn = QtWidgets.QPushButton("Create VRay Ptex")
        self.create_displacement_btn = QtWidgets.QPushButton("Create Displacement")
        self.cc_node_finder = QtWidgets.QPushButton("CC Node Finder")

    def create_layout(self):
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)

        main_layout.addWidget(self.material_builder_btn)
        main_layout.addWidget(self.create_texture_btn)
        main_layout.addWidget(self.create_ptex_btn)
        main_layout.addWidget(self.create_cc_btn)
        main_layout.addWidget(self.cc_node_finder)
        main_layout.addWidget(self.create_displacement_btn)
        main_layout.addStretch()

    def create_connections(self):
        self.material_builder_btn.clicked.connect(self.material_builder_btn_callback)
        self.create_cc_btn.clicked.connect(self.create_cc_btn_callback)
        self.cc_node_finder.clicked.connect(self.cc_node_finder_callback)
        self.create_texture_btn.clicked.connect(self.create_texture_btn_callback)
        self.create_ptex_btn.clicked.connect(self.create_ptex_btn_callback)
        self.create_displacement_btn.clicked.connect(self.create_displacement_btn_callback)

    def material_builder_btn_callback(self):
        material_builder_ui.main()

    def cc_node_finder_callback(self):
        cc_node_editor_ui.main()

    def create_cc_btn_callback(self):
        if pm.ls(sl=1):
            material_utils.create_cc_node(pm.ls(sl=1)[0])
        else:
            material_utils.create_cc_node()

    def create_texture_btn_callback(self):
        material_utils.create_texture()

    def create_ptex_btn_callback(self):
        material_utils.create_texture(ptex=1)

    def create_displacement_btn_callback(self):
        if pm.ls(sl=1):
            for obj in pm.ls(sl=1):
                material_utils.create_displacement_node(name=str(obj), obj=obj)
        else:
            material_utils.create_displacement_node()


def main():
    try:
        cmds.deleteUI("LookdevToolkitUI")
    except Exception:
        pass

    dialog = LookdevToolkitUI()
    dialog.show()


if __name__ == "__main__":
    main()
