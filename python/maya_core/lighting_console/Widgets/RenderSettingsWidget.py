from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import pymel.core as pm
import vray

from pyqt_commons import MWidgets

reload(MWidgets)

from maya_core.lighting_console.constants import *


# TODO Combine all settings
# TODO Aspect Ratio Lock


class RenderOverridesWidget(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)

    def __init__(self, *args, **kwargs):
        super(RenderOverridesWidget, self).__init__(*args, **kwargs)

        self.setContentsMargins(0, 0, 0, 0)
        self.vray_settings = pm.PyNode("vraySettings")

        self.setObjectName("RenderOverridesWidget")

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.displacement_override_cb = QtWidgets.QCheckBox("Displacement")
        self.subdivision_ovveride_cb = QtWidgets.QCheckBox("Subdivision")

        self.displacement_override_cb.setChecked(self.vray_settings.globopt_geom_displacement.get())
        self.subdivision_ovveride_cb.setChecked(self.vray_settings.globopt_subdivision.get())

    def create_layout(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setSpacing(0)

        geo_overrides_layout = QtWidgets.QVBoxLayout()
        geo_overrides_layout.setSpacing(0)

        geo_overrides_layout.addWidget(self.displacement_override_cb)
        geo_overrides_layout.addWidget(self.subdivision_ovveride_cb)

        main_layout.addLayout(geo_overrides_layout)

    def create_connections(self):
        self.displacement_override_cb.stateChanged.connect(
            lambda: self.vray_settings.globopt_geom_displacement.set(self.displacement_override_cb.isChecked()))
        self.subdivision_ovveride_cb.stateChanged.connect(
            lambda: self.vray_settings.globopt_subdivision.set(self.subdivision_ovveride_cb.isChecked()))


class RenderSettings(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)

    def __init__(self, width, height, *args, **kwargs):
        super(RenderSettings, self).__init__(*args, **kwargs)

        self.width = width
        self.height = height
        self.setContentsMargins(0, 0, 0, 0)

        self.vray_settings = pm.PyNode("vraySettings")

        self.setFixedHeight(self.height)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.render_cam_lbl = QtWidgets.QLabel("Render Cam: ")
        self.render_cam_cmbx = QtWidgets.QComboBox()
        self.render_cam_cmbx.setFixedWidth(150)
        self.get_current_cameras()

        self.res_x_lbl = QtWidgets.QLabel("Width: ")
        self.res_y_lbl = QtWidgets.QLabel("Height: ")

        self.res_x_le = QtWidgets.QLineEdit()
        self.res_y_le = QtWidgets.QLineEdit()

        self.res_x_le.setFixedWidth(80)
        self.res_y_le.setFixedWidth(80)
        # self.res_y_le.setMaximumWidth(self.width * .2)

        self.res_x_le.setAlignment(QtCore.Qt.AlignRight)
        self.res_y_le.setAlignment(QtCore.Qt.AlignRight)

        self.get_resolution()

        self.overrides_widget = RenderOverridesWidget()

        self.threshold_lbl = QtWidgets.QLabel("Noise Threshold: ")
        self.threshold_le = QtWidgets.QLineEdit()
        self.threshold_le.setFixedWidth(80)
        self.threshold_le.setAlignment(QtCore.Qt.AlignRight)

        self.get_threshold()

    def get_threshold(self):
        if self.vray_settings.samplerType.get() == 4:
            threshold = self.vray_settings.dmcThreshold.get()
        else:
            threshold = self.vray_settings.progressiveThreshold.get()
        self.threshold_le.setText("{:.3f}".format(threshold))

    def get_current_cameras(self):
        self.cameras = []
        all_cameras = pm.ls(type="camera")

        render_cam = "persp"

        for cam in all_cameras:
            cam = pm.PyNode(cam)

            if cam.startswith("front") or cam.startswith("side") or cam.startswith("top"):
                try:
                    cam.renderable.set(0)
                except Exception:
                    pass
                continue

            self.render_cam_cmbx.addItem(str(cam).replace("Shape", ""))

            self.cameras.append(cam)

            if cam.renderable.get():
                self.render_cam_cmbx.setCurrentText(str(cam).replace("Shape", ""))

    def create_layout(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.addStretch()

        render_cam_layout = QtWidgets.QHBoxLayout()

        render_cam_layout.addWidget(self.render_cam_lbl)
        render_cam_layout.addWidget(self.render_cam_cmbx)

        cam_tresh_layout = QtWidgets.QVBoxLayout()
        cam_tresh_layout.addLayout(render_cam_layout)

        thresh_layout = QtWidgets.QHBoxLayout()
        thresh_layout.setSpacing(0)
        thresh_layout.addStretch()
        thresh_layout.addWidget(self.threshold_lbl)
        thresh_layout.addWidget(self.threshold_le)

        cam_tresh_layout.addLayout(thresh_layout)

        main_layout.addLayout(cam_tresh_layout)

        main_layout.addWidget(MWidgets.QVLine())

        res_lbl_layout = QtWidgets.QVBoxLayout()
        res_lbl_layout.setSpacing(0)
        res_lbl_layout.addWidget(self.res_x_lbl)
        res_lbl_layout.addWidget(self.res_y_lbl)

        main_layout.addLayout(res_lbl_layout)

        res_le_layout = QtWidgets.QVBoxLayout()
        res_le_layout.setSpacing(0)
        res_le_layout.addWidget(self.res_x_le)
        res_le_layout.addWidget(self.res_y_le)

        main_layout.addLayout(res_le_layout)

        main_layout.addWidget(MWidgets.QVLine())
        main_layout.addWidget(self.overrides_widget)

    def create_connections(self):
        self.render_cam_cmbx.currentIndexChanged.connect(self.set_render_cam)
        self.res_x_le.returnPressed.connect(self.set_resolution)
        self.res_y_le.returnPressed.connect(self.set_resolution)
        self.threshold_le.returnPressed.connect(self.set_threshold)

    def set_threshold(self):
        try:
            if self.vray_settings.samplerType.get() == 4:
                threshold = self.vray_settings.dmcThreshold.set(float(self.threshold_le.text()))
            else:
                threshold = self.vray_settings.progressiveThreshold.set(float(self.threshold_le.text()))
        except Exception:
            if self.vray_settings.samplerType.get() == 4:
                threshold = self.vray_settings.dmcThreshold.get()
            else:
                threshold = self.vray_settings.progressiveThreshold.get()

        self.get_threshold()

    def set_render_cam(self):
        render_cam = pm.PyNode(self.render_cam_cmbx.currentText())

        for cam in pm.ls(type="camera"):
            if str(cam).replace("Shape", "") == str(render_cam):
                cam.renderable.set(1)
            else:
                cam.renderable.set(0)

    def get_resolution(self):
        settings = pm.PyNode("vraySettings")

        self.res_x_le.setText(str(settings.width.get()))
        self.res_y_le.setText(str(settings.height.get()))

    def set_resolution(self):
        settings = pm.PyNode("vraySettings")

        try:
            x = float(self.res_x_le.text())
            y = float(self.res_y_le.text())
        except Exception:
            return

        settings.width.set(x)
        settings.height.set(y)

        cmds.setAttr("defaultResolution.width", x)
        cmds.setAttr("defaultResolution.height", y)
        cmds.setAttr("defaultResolution.deviceAspectRatio", (x / y))
        cmds.setAttr("defaultResolution.lockDeviceAspectRatio", 0)
        cmds.setAttr("defaultResolution.pixelAspect", 1.0)

        settings.aspectRatio.set(float(x) / float(y))


class RenderSettingsWidget(QtWidgets.QWidget):
    pass
