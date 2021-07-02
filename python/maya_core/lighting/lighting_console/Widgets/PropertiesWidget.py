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

reload(MWidgets)
reload(re_constants)

from maya_core.common_tools import logger

log = logger.Logger()

INDENT = 40


class CheckBoxAttrWidget(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)

    def __init__(self, node, attr_data, *args, **kwargs):
        super(CheckBoxAttrWidget, self).__init__(*args, **kwargs)

        self.setContentsMargins(INDENT * 2, 0, 0, 0)

        self.pm_node = node
        self.attr_data = attr_data
        self.attr = self.attr_data['name']
        self.setObjectName("{0}.{1}".format(str(self.pm_node), self.attr))

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
        log.info("PropertiesWidget, CheckBoxAttrWidget, set_attr")

        getattr(self.pm_node, self.attr).set(self.cb.isChecked())

        current_rl = cmds.editRenderLayerGlobals(q=True, crl=True)

        if current_rl != "defaultRenderLayer":
            cmds.editRenderLayerAdjustment("{0}.{1}".format(str(self.pm_node), self.attr))

    def refresh_attr(self):
        log.info("PropertiesWidget, CheckBoxAttrWidget, refresh_attr")

        value = getattr(self.pm_node, self.attr).get()

        self.cb.setChecked(value)


class LineEditAttrWidget(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)

    def __init__(self, node, attr_data, *args, **kwargs):
        super(LineEditAttrWidget, self).__init__(*args, **kwargs)
        self.setContentsMargins(INDENT, 0, 0, 0)

        self.pm_node = node
        self.attr_data = attr_data
        self.attr = self.attr_data['name']
        self.setObjectName("{0}.{1}".format(str(self.pm_node), self.attr))

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
        self.le.setFixedWidth(270)

    def create_layout(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(self.lbl)
        main_layout.addWidget(self.le)
        main_layout.addStretch()

    def create_connections(self):
        self.le.returnPressed.connect(self.set_attr)

    def set_attr(self):
        log.info("PropertiesWidget, LineEditAttrWidget, set_attr")

        try:
            getattr(self.pm_node, self.attr).set(self.le.text())
        except Exception:
            pass

        value = getattr(self.pm_node, self.attr).get()

        self.le.setText(str(value))

        current_rl = cmds.editRenderLayerGlobals(q=True, crl=True)

        if current_rl != "defaultRenderLayer":
            cmds.editRenderLayerAdjustment("{0}.{1}".format(str(self.pm_node), self.attr))

    def refresh_attr(self):
        log.info("PropertiesWidget, LineEditAttrWidget, refresh_attr")

        value = getattr(self.pm_node, self.attr).get()
        self.le.setText(str(value))


class ComboBoxAttrWidget(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)

    def __init__(self, node, attr_data, *args, **kwargs):
        super(ComboBoxAttrWidget, self).__init__(*args, **kwargs)
        self.setContentsMargins(INDENT, 0, 0, 0)

        self.pm_node = node
        self.attr_data = attr_data
        self.attr = self.attr_data['name']
        self.setObjectName("{0}.{1}".format(str(self.pm_node), self.attr))

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
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(self.lbl)
        main_layout.addWidget(self.cmbx)
        main_layout.addStretch()

    def create_connections(self):
        self.cmbx.currentIndexChanged.connect(self.set_attr)

    def set_attr(self):
        log.info("PropertiesWidget, ComboBoxAttrWidget, set_attr")

        getattr(self.pm_node, self.attr).set(self.cmbx.currentIndex())

        current_rl = cmds.editRenderLayerGlobals(q=True, crl=True)

        if current_rl != "defaultRenderLayer":
            cmds.editRenderLayerAdjustment("{0}.{1}".format(str(self.pm_node), self.attr))

    def refresh_attr(self):
        log.info("PropertiesWidget, ComboBoxAttrWidget, refresh_attr")

        value = getattr(self.pm_node, self.attr).get()
        self.cmbx.setCurrentIndex(value)


class SliderAttrWidget(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)

    def __init__(self, node, attr_data, *args, **kwargs):
        super(SliderAttrWidget, self).__init__(*args, **kwargs)
        self.setContentsMargins(INDENT, 0, 20, 0)

        self.pm_node = node
        self.attr_data = attr_data
        self.attr = self.attr_data['name']
        self.get_value()

        self.setObjectName("{0}.{1}".format(str(self.pm_node), self.attr))

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
        self.le.setFixedWidth(100)

        self.slider = QtWidgets.QSlider()
        self.slider.setFixedWidth(175)
        self.slider.setRange(self.attr_data['values'][0], self.attr_data['values'][1])
        self.slider.setOrientation(QtCore.Qt.Horizontal)

    def create_layout(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(self.lbl)
        main_layout.addWidget(self.le)
        main_layout.addWidget(self.slider)
        main_layout.addStretch()

    def create_connections(self):
        self.le.returnPressed.connect(self.le_returnPressed_callback)
        self.slider.sliderMoved.connect(self.slider_sliderMoved_callback)

    def refresh_attr(self):
        log.info("PropertiesWidget, SliderAttrWidget, refresh_attr")

        self.le.setText(str(self.value))
        self.slider.setValue(self.value)

    def get_value(self):
        log.info("PropertiesWidget, SliderAttrWidget, get_value")

        self.value = getattr(self.pm_node, self.attr).get()
        return self.value

    def set_attr(self):
        log.info("PropertiesWidget, SliderAttrWidget, set_attr")

        getattr(self.pm_node, self.attr).set(self.value)

        current_rl = cmds.editRenderLayerGlobals(q=True, crl=True)

        if current_rl != "defaultRenderLayer":
            cmds.editRenderLayerAdjustment("{0}.{1}".format(str(self.pm_node), self.attr))

    def le_returnPressed_callback(self):
        log.info("PropertiesWidget, SliderAttrWidget, le_returnPressed_callback")

        try:
            self.value = int(self.le.text())
            self.slider.setValue(self.value)
            self.set_attr()
        except Exception:
            self.refresh_attr()

    def slider_sliderMoved_callback(self, value):
        log.info("PropertiesWidget, SliderAttrWidget, slider_sliderMoved_callback")

        try:
            self.value = value
            self.le.setText(str(self.value))
            self.set_attr()
        except Exception:
            self.refresh_attr()


class DoubleSliderAttrWidget(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)

    def __init__(self, node, attr_data, *args, **kwargs):
        super(DoubleSliderAttrWidget, self).__init__(*args, **kwargs)
        self.setContentsMargins(INDENT, 0, 20, 0)

        self.pm_node = node
        self.attr_data = attr_data
        self.attr = self.attr_data['name']
        self.get_value()
        self.setObjectName("{0}.{1}".format(str(self.pm_node), self.attr))

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
        self.le.setFixedWidth(100)

        self.slider = MWidgets.DoubleSlider()
        self.slider.setFixedWidth(175)
        self.slider.setMinimum(self.attr_data['values'][0])
        self.slider.setMaximum(self.attr_data['values'][1])
        self.slider.setOrientation(QtCore.Qt.Horizontal)

    def create_layout(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 5, 0)

        main_layout.addWidget(self.lbl)
        main_layout.addWidget(self.le)
        main_layout.addWidget(self.slider)
        main_layout.addStretch()

    def create_connections(self):
        self.le.returnPressed.connect(self.le_returnPressed_callback)
        self.slider.doubleValueChanged.connect(self.slider_sliderMoved_callback)

    def refresh_attr(self):
        log.info("PropertiesWidget, DoubleSliderAttrWidget, refresh_attr")
        self.le.blockSignals(True)
        self.slider.blockSignals(True)

        self.le.setText(str(self.value))
        self.slider.setValue(self.value)

        self.le.blockSignals(False)
        self.slider.blockSignals(False)

    def get_value(self):
        log.info("PropertiesWidget, DoubleSliderAttrWidget, get_value")

        self.value = getattr(self.pm_node, self.attr).get()
        return self.value

    def set_attr(self):
        log.info("PropertiesWidget, DoubleSliderAttrWidget, set_attr")

        getattr(self.pm_node, self.attr).set(self.value)

        current_rl = cmds.editRenderLayerGlobals(q=True, crl=True)

        if current_rl != "defaultRenderLayer":
            cmds.editRenderLayerAdjustment("{0}.{1}".format(str(self.pm_node), self.attr))

    def le_returnPressed_callback(self):
        log.info("PropertiesWidget, DoubleSliderAttrWidget, le_returnPressed_callback")
        self.le.blockSignals(True)
        self.slider.blockSignals(True)

        try:
            self.value = int(self.le.text())
            self.slider.setValue(self.value)
            self.set_attr()
        except Exception:
            self.refresh_attr()

        self.le.blockSignals(False)
        self.slider.blockSignals(False)

    def slider_sliderMoved_callback(self, value):
        log.info("PropertiesWidget, DoubleSliderAttrWidget, slider_sliderMoved_callback")
        self.le.blockSignals(True)
        self.slider.blockSignals(True)

        try:
            self.value = value
            self.le.setText(str(self.value))
            self.set_attr()
        except Exception:
            self.refresh_attr()

        self.le.blockSignals(False)
        self.slider.blockSignals(False)


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

        main_layout.addLayout(self.properties_cw)
        main_layout.addStretch()

    def create_connections(self):
        pass

    def set_properties(self, properties_widget):
        log.info("PropertiesWidget, PropertiesWidget, set_properties")

        for i in range(self.properties_cw.count()):
            widget = self.properties_cw.itemAt(i).widget()

            if widget:
                widget.setVisible(False)
                self.properties_cw.removeWidget(widget)

        if properties_widget is not None:
            self.properties_widget = properties_widget
            self.properties_widget.setVisible(True)
            self.properties_cw.addWidget(self.properties_widget)
            self.properties_widget.refresh_attr()
