from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import pymel.core as pm
import vray

from pyqt_commons import MWidgets

from maya_core.lighting_console.constants import *

reload(MWidgets)


class AOVsWidget(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)

    def __init__(self, *args, **kwargs):
        super(AOVsWidget, self).__init__(*args, **kwargs)

        self.setObjectName("AOVsWidget")

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.setContentsMargins(0, 0, 0, 0)

    def create_actions(self):
        pass

    def create_widgets(self):
        self.aovs_header_lbl = MWidgets.HeaderLabel("AOVs")

        self.aovs_create_tw = QtWidgets.QTreeWidget()
        aovs_create_header_item = QtWidgets.QTreeWidgetItem(["Create Render Pass"])
        self.aovs_create_tw.setHeaderItem(aovs_create_header_item)

        self.aovs_tw = QtWidgets.QTreeWidget()
        aovs_header_item = QtWidgets.QTreeWidgetItem(["Render Passes"])
        self.aovs_tw.setHeaderItem(aovs_header_item)

        aov_items = [
            "Diffuse",
            "Light Select",
            "Multi Matte",
            "Extra Tex",
            "Reflection",
            "Refraction",
            "Specular",
            "Velocity",
            "Z-Depth",
            "Normals"
        ]

        for aov in sorted(aov_items):
            item = QtWidgets.QTreeWidgetItem()
            item.setText(0, aov)
            self.aovs_create_tw.addTopLevelItem(item)

    def create_layout(self):
        aovs_layout = QtWidgets.QVBoxLayout(self)
        aovs_layout.setSpacing(GLOBAL_SPACING)

        aovs_layout.addWidget(self.aovs_header_lbl)

        aovs_tw_layout = QtWidgets.QHBoxLayout()
        aovs_tw_layout.setSpacing(GLOBAL_SPACING)

        aovs_tw_layout.addWidget(self.aovs_create_tw)
        aovs_tw_layout.addWidget(self.aovs_tw)

        aovs_layout.addLayout(aovs_tw_layout)

    def create_connections(self):
        pass
