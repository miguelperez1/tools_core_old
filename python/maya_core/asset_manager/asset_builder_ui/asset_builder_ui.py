from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import maya.cmds as cmds

import os
import sys
import subprocess

from pyqt_commons import MWidgets


def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class AssetBuilder(QtWidgets.QDialog):
    """
    Dialog used to demonstrates many of the standard dialogs available in Qt
    """

    def __init__(self, parent=maya_main_window()):
        super(AssetBuilder, self).__init__(parent)

        self.setWindowTitle("Asset Builder")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.setFixedSize(500, 400)
        self.setStyleSheet("F:\share\tools\core\pyqt_commons\stylesheet.qss")

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.asset_class_lbl = QtWidgets.QLabel('Asset Class:')

        self.asset_classes = ['Simple', 'Standard']
        self.asset_class_cmbx = QtWidgets.QComboBox()
        self.asset_class_cmbx.addItems(self.asset_classes)

        self.asset_name_lbl = QtWidgets.QLabel('Asset Name:')
        self.asset_name_le = QtWidgets.QLineEdit()

        self.asset_type_lbl = QtWidgets.QLabel('Asset Type:')
        self.asset_type_cmbx = QtWidgets.QComboBox()

        asset_types = ['Character', 'Prop', 'Set', 'Transit', 'Material']

        self.asset_type_cmbx.addItems(asset_types)

        self.scale_lbl = QtWidgets.QLabel('Scale in ft:')
        self.scale_le = QtWidgets.QLineEdit()

        self.build_rig_cb = QtWidgets.QCheckBox('Build Rig')
        self.build_rig_cb.setChecked(True)

        self.ok_btn = QtWidgets.QPushButton('Build')
        self.cancel_btn = QtWidgets.QPushButton('Cancel')

    def create_layout(self):
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)

        asset_class_layout = QtWidgets.QHBoxLayout()
        asset_class_layout.addWidget(self.asset_class_lbl)
        asset_class_layout.addWidget(self.asset_class_cmbx)
        asset_class_layout.addStretch()

        asset_details_layout = QtWidgets.QHBoxLayout()
        asset_details_layout.addWidget(self.asset_name_lbl)
        asset_details_layout.addWidget(self.asset_name_le)
        asset_details_layout.addWidget(self.asset_type_lbl)
        asset_details_layout.addWidget(self.asset_type_cmbx)
        asset_details_layout.addStretch()

        scale_layout = QtWidgets.QHBoxLayout()
        scale_layout.addWidget(self.scale_lbl)
        scale_layout.addWidget(self.scale_le)
        scale_layout.addStretch()

        options_layout = QtWidgets.QHBoxLayout()
        options_layout.addWidget(self.build_rig_cb)
        options_layout.addStretch()

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(asset_class_layout)
        main_layout.addLayout(asset_details_layout)
        main_layout.addWidget(MWidgets.QHLine())
        main_layout.addLayout(scale_layout)
        main_layout.addWidget(QtWidgets.QLabel('Options'))
        main_layout.addLayout(options_layout)
        main_layout.addStretch()

        main_layout.addLayout(btn_layout)

    def create_connections(self):
        self.cancel_btn.clicked.connect(self.close)


if __name__ == "maya_core.asset_manager.asset_builder_ui.asset_builder_ui":

    try:
        example_dialog.close()  # pylint: disable=E0601
        example_dialog.deleteLater()
    except:
        pass

    example_dialog = AssetBuilder()
    example_dialog.show()

    cmds.polySphere()
