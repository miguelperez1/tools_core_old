from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import pymel.core as pm
import vray
import re

from pyqt_commons import MWidgets

reload(MWidgets)

from maya_core.lighting_console.constants import *
from maya_core.lighting_console import re_constants

reload(re_constants)

INDENT = 40


class CheckBoxAttrWidget(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)

    def __init__(self, node, attr, *args, **kwargs):
        super(CheckBoxAttrWidget, self).__init__(*args, **kwargs)

        self.setContentsMargins(INDENT, 0, 0, 0)

        self.pm_node = node
        self.class_type = self.pm_node.vrayClassType.get()
        self.attr = attr
        self.attr_data = re_constants.VRayRenderElementsAttributes[self.class_type][self.attr]

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.cb = QtWidgets.QCheckBox()
        self.cb.setText(self.attr_data['label'])

        self.cb.setChecked(getattr(self.pm_node, self.attr).get())

    def create_layout(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.cb)
        main_layout.addStretch()

    def create_connections(self):
        self.cb.stateChanged.connect(self.set_attr)

    def set_attr(self):
        getattr(self.pm_node, self.attr).set(self.cb.isChecked())

    def refresh_attr(self):
        value = getattr(self.pm_node, self.attr).get()

        self.cb.setChecked(value)


class LineEditAttrWidget(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)

    def __init__(self, node, attr, *args, **kwargs):
        super(LineEditAttrWidget, self).__init__(*args, **kwargs)
        self.setContentsMargins(INDENT, 0, 0, 0)

        self.pm_node = node
        self.class_type = self.pm_node.vrayClassType.get()
        self.attr = attr
        self.attr_data = re_constants.VRayRenderElementsAttributes[self.class_type][self.attr]

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.lbl = QtWidgets.QLabel()

        self.lbl.setText(self.attr_data['label'])

        self.le = QtWidgets.QLineEdit()
        self.le.setText(str(getattr(self.pm_node, self.attr).get()))

    def create_layout(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(self.lbl)
        main_layout.addWidget(self.le)
        main_layout.addStretch()

    def create_connections(self):
        self.le.returnPressed.connect(self.set_attr)

    def set_attr(self):
        try:
            getattr(self.pm_node, self.attr).set(self.le.text())
        except Exception:
            pass

        value = getattr(self.pm_node, self.attr).get()

        self.le.setText(str(value))

    def refresh_attr(self):
        value = getattr(self.pm_node, self.attr).get()
        self.le.setText(str(value))


class ComboBoxAttrWidget(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)

    def __init__(self, node, attr, *args, **kwargs):
        super(ComboBoxAttrWidget, self).__init__(*args, **kwargs)
        self.setContentsMargins(INDENT, 0, 0, 0)

        self.pm_node = node
        self.class_type = self.pm_node.vrayClassType.get()
        self.attr = attr
        self.attr_data = re_constants.VRayRenderElementsAttributes[self.class_type][self.attr]

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.cmbx = QtWidgets.QComboBox()
        self.lbl = QtWidgets.QLabel()

        self.lbl.setText(self.attr_data['label'])
        self.cmbx.addItems(self.attr_data['values'])

    def create_layout(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(self.lbl)
        main_layout.addWidget(self.cmbx)
        main_layout.addStretch()

    def create_connections(self):
        self.cmbx.currentIndexChanged.connect(self.set_attr)

    def set_attr(self):
        getattr(self.pm_node, self.attr).set(self.cmbx.currentIndex())

    def refresh_attr(self):
        value = getattr(self.pm_node, self.attr).get()
        self.cmbx.setCurrentIndex(value)


class PropertiesWidget(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)

    def __init__(self, *args, **kwargs):
        super(PropertiesWidget, self).__init__(*args, **kwargs)

        self.setObjectName("PropertiesWidget")

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.properties_header_lbl = MWidgets.HeaderLabel("Properties")

        self.tmp_info_lbl = QtWidgets.QLabel()

        self.properties_cw = QtWidgets.QVBoxLayout()

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.addWidget(self.properties_header_lbl)
        main_layout.addWidget(MWidgets.QHLine())

        main_layout.addLayout(self.properties_cw)
        main_layout.addStretch()

    def create_connections(self):
        pass

    def set_properties(self, properties_widget):
        for i in range(self.properties_cw.count()):
            widget = self.properties_cw.itemAt(i).widget()

            if widget:
                widget.setVisible(False)
                self.properties_cw.removeWidget(widget)

        if properties_widget:
            properties_widget.setVisible(True)
            self.properties_cw.addWidget(properties_widget)
            properties_widget.refresh_attr()
