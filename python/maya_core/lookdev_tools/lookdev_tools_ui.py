from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import maya.cmds as cmds

from pyqt_commons import MWidgets

from maya_core.material_builder import material_builder_ui
from maya_core.lookdev_tools import create_cc_node
from maya_core.lookdev_tools import cc_node_editor_ui
from maya_core.common_tools import logger
from maya_core.asset_manager.texture_manager import texture_manager_ui

log = logger.Logger()

reload(material_builder_ui)
reload(create_cc_node)
reload(cc_node_editor_ui)
reload(texture_manager_ui)


class LookDevToolsWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=MWidgets.maya_main_window()):
        super(LookDevToolsWindow, self).__init__(parent)

        self.setWindowTitle("LookDev Tools")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setFixedWidth(400)

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.ld_header = MWidgets.HeaderLabel("LookDev Tools")

        self.import_lookdev_light_rig_btn = QtWidgets.QPushButton("Import LookDev Light Rig")

        self.material_builder_btn = QtWidgets.QPushButton("Material Builder")

        self.create_cc_node_btn = QtWidgets.QPushButton("Create CC Node")
        self.cc_node_editor_btn = QtWidgets.QPushButton("CC Node Editor")

        self.create_displacement_nodes_btn = QtWidgets.QPushButton("Create Displacement Nodes")

        self.texture_asset_manager_btn = QtWidgets.QPushButton("Texture Manager")

    def create_layout(self):
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)

        main_layout.addWidget(self.ld_header)
        main_layout.addWidget(MWidgets.QHLine())
        main_layout.addWidget(MWidgets.QHLine())
        main_layout.addWidget(self.import_lookdev_light_rig_btn)
        main_layout.addWidget(MWidgets.QHLine())
        main_layout.addWidget(self.texture_asset_manager_btn)
        main_layout.addWidget(MWidgets.QHLine())
        main_layout.addWidget(self.material_builder_btn)
        main_layout.addWidget(MWidgets.QHLine())
        main_layout.addWidget(self.create_cc_node_btn)
        main_layout.addWidget(MWidgets.QHLine())
        main_layout.addWidget(self.cc_node_editor_btn)
        main_layout.addWidget(MWidgets.QHLine())
        main_layout.addWidget(self.create_displacement_nodes_btn)
        main_layout.addStretch()

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
        self.import_lookdev_light_rig_btn.clicked.connect(self.import_lookdev_light_rig_btn_callback)
        self.material_builder_btn.clicked.connect(self.material_builder_btn_callback)
        self.texture_asset_manager_btn.clicked.connect(self.texture_asset_manager_btn_callback)
        self.create_cc_node_btn.clicked.connect(self.create_cc_node_btn_callback)
        self.cc_node_editor_btn.clicked.connect(self.cc_node_editor_btn_callback)
        self.create_displacement_nodes_btn.clicked.connect(self.create_displacement_nodes_btn_callback)

    def import_lookdev_light_rig_btn_callback(self):
        cmds.file(r"F:\share\assets\maya\lookdev_kit.ma", i=True)

    def material_builder_btn_callback(self):
        reload(material_builder_ui)
        material_builder_ui.main()

    def create_cc_node_btn_callback(self):
        reload(create_cc_node)
        create_cc_node.main()

    def cc_node_editor_btn_callback(self):
        reload(cc_node_editor_ui)
        cc_node_editor_ui.main()

    def create_displacement_nodes_btn_callback(self):
        log.warning("TO DO create_displacement_nodes_btn_callback")

    def texture_asset_manager_btn_callback(self):
        reload(texture_manager_ui)
        texture_manager_ui.main()


def main():
    try:
        dialog.close()
        dialog.deleteLater()
    except:
        pass

    dialog = LookDevToolsWindow()
    dialog.show()


if __name__ == "__main__":
    main()
