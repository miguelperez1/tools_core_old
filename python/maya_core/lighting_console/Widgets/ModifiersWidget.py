from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import pymel.core as pm
import vray

from pyqt_commons import MWidgets

reload(MWidgets)

from maya_core.lighting_console.constants import *


class ModifiersWidget(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)

    def __init__(self, *args, **kwargs):
        super(ModifiersWidget, self).__init__(*args, **kwargs)

        self.setObjectName("ModifiersWidget")

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.setContentsMargins(0, 0, 0, 0)

    def create_actions(self):
        pass

    def create_widgets(self):
        self.modifiers_header_lbl = MWidgets.HeaderLabel("Modifiers")

        self.modifiers_add_btn = QtWidgets.QPushButton("+")
        self.modifiers_add_btn.setFixedSize(30, 30)

        self.modifiers_remove_btn = QtWidgets.QPushButton("-")
        self.modifiers_remove_btn.setFixedSize(30, 30)

        self.modifiers_duplicate_btn = MWidgets.ImagePushButton(30, 30)
        self.modifiers_duplicate_btn.set_image("F:\\share\\tools\\shelf_icons\\duplicate.png")
        self.modifiers_duplicate_btn.setFixedSize(30, 30)

        self.modifiers_tw = QtWidgets.QTreeWidget()
        modifiers_tw_header = QtWidgets.QTreeWidgetItem(['Modifier', 'Type'])
        self.modifiers_tw.setHeaderItem(modifiers_tw_header)

        self.linked_sets_tw = QtWidgets.QTreeWidget()
        linked_sets_tw_header = QtWidgets.QTreeWidgetItem(['Connected Sets'])
        self.linked_sets_tw.setHeaderItem(linked_sets_tw_header)
        self.linked_sets_tw.setMaximumHeight(RES_Y * .15)

    def create_layout(self):
        modifiers_layout = QtWidgets.QVBoxLayout(self)
        modifiers_layout.setSpacing(GLOBAL_SPACING)

        modifiers_btn_layout = QtWidgets.QHBoxLayout()
        modifiers_btn_layout.setSpacing(GLOBAL_SPACING)

        modifiers_btn_layout.addWidget(self.modifiers_header_lbl)
        modifiers_btn_layout.addStretch()
        modifiers_btn_layout.addWidget(self.modifiers_add_btn)
        modifiers_btn_layout.addWidget(self.modifiers_remove_btn)
        modifiers_btn_layout.addWidget(self.modifiers_duplicate_btn)

        modifiers_layout.addLayout(modifiers_btn_layout)

        modifiers_layout.addWidget(self.modifiers_tw)
        modifiers_layout.addWidget(self.linked_sets_tw)

    def create_connections(self):
        pass
