from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import maya.cmds as cmds

from maya_core.common_tools import logger
from maya_core import material_builder
from maya_core.material_builder import MaterialBuilderWidget

import os

log = logger.Logger()


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class QHLine(QtWidgets.QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)


class BuilderWindow(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(BuilderWindow, self).__init__(parent)

        self.setWindowTitle("VRay Material Builder")
        self.setObjectName("MaterialBuilderUI")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.valid_asset_name = False
        self.valid_mesh = False

        self.setMinimumWidth(500)
        self.setMinimumHeight(400)

        self.texture_types = ['']

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.material_buidlder_widget = MaterialBuilderWidget.MaterialBuilderWidget()

        # Build button
        self.build_btn = QtWidgets.QPushButton('Build')
        self.cancel_btn = QtWidgets.QPushButton('Cancel')

    def create_layout(self):
        # button layout
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.build_btn)
        button_layout.addWidget(self.cancel_btn)

        # Main Layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.material_buidlder_widget)
        main_layout.addLayout(button_layout)

    def create_connections(self):
        # Cancel
        self.cancel_btn.clicked.connect(self.close)

        # Build
        self.build_btn.clicked.connect(self.build_material)

    def build_material(self):
        self.material_buidlder_widget.build_material()

        self.close()


def main():
    try:
        cmds.deleteUI("MaterialBuilderUI")
    except Exception:
        pass

    asset_builder_dialog = BuilderWindow()
    asset_builder_dialog.show()


if __name__ == "__main__":
    main()
