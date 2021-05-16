from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import pymel.core as pm
import vray

from pyqt_commons import MWidgets

reload(MWidgets)

from maya_core.lighting_console.constants import *


class PropertiesWidget(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)

    def __init__(self, *args, **kwargs):
        super(PropertiesWidget, self).__init__(*args, **kwargs)

        self.setObjectName("PropertiesWidget")

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.setContentsMargins(0, 0, 0, 0)

    def create_actions(self):
        pass

    def create_widgets(self):
        self.properties_header_lbl = MWidgets.HeaderLabel("Properties")

        self.tmp_info_lbl = QtWidgets.QLabel()
        self.tmp_info_lbl.setText("Lights: color, intensity/exp, temp, tex, directional"
                                  "Render Layer")

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(GLOBAL_SPACING)

        main_layout.addWidget(self.properties_header_lbl)
        main_layout.addWidget(self.tmp_info_lbl)
        main_layout.addStretch()

    def create_connections(self):
        pass

    def set_properties(self, item):
        print "{0} : {1}".format(item, type(item))
