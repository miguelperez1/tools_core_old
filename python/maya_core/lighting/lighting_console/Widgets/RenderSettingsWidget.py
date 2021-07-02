from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import pymel.core as pm
import vray

from pyqt_commons import MWidgets

reload(MWidgets)

from maya_core.lighting_console.constants import *

# TODO Script Jobs

class RenderSettingsWidget(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)

    def __init__(self, *args, **kwargs):
        super(RenderSettingsWidget, self).__init__(*args, **kwargs)

        self.setContentsMargins(0, 0, 0, 0)
        self.vray_settings = pm.PyNode("vraySettings")

        self.setObjectName("RenderSettingsWidget")

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        icon_scale = .45

        self.render_cam_cmbx = QtWidgets.QComboBox()
        self.render_cam_lbl = QtWidgets.QLabel("Render Cam: ")
        self.render_cam_cmbx.setFixedWidth(150)
        self.get_current_cameras()

        self.threshold_lbl = QtWidgets.QLabel("Noise Threshold: ")
        self.threshold_le = QtWidgets.QLineEdit()
        self.threshold_le.setFixedWidth(80)
        self.threshold_le.setAlignment(QtCore.Qt.AlignRight)
        self.get_threshold()

        self.res_x_lbl = QtWidgets.QLabel("Width: ")
        self.res_x_le = QtWidgets.QLineEdit()

        self.res_y_lbl = QtWidgets.QLabel("Height: ")
        self.res_y_le = QtWidgets.QLineEdit()

        self.res_x_le.setFixedWidth(80)
        self.res_y_le.setFixedWidth(80)

        self.res_x_le.setAlignment(QtCore.Qt.AlignRight)
        self.res_y_le.setAlignment(QtCore.Qt.AlignRight)

        self.get_resolution()

        self.res_asplock_img_btn = MWidgets.ImagePushButton(35, 70)
        if self.vray_settings.aspectLock.get():
            self.res_asplock_img_btn.set_image("F:\\share\\tools\\shelf_icons\\linked.png", .75)
        else:
            self.res_asplock_img_btn.set_image("F:\\share\\tools\\shelf_icons\\unlinked.png", .75)
        self.res_asplock_img_btn.setToolTip("Lock Aspect Ratio")

        self.ovrd_displacement_cb = QtWidgets.QCheckBox("Displacement")
        self.ovrd_displacement_cb.setChecked(self.vray_settings.globopt_geom_displacement.get())

        self.ovrd_subdivision_cb = QtWidgets.QCheckBox("Subdivision")
        self.ovrd_subdivision_cb.setChecked(self.vray_settings.globopt_subdivision.get())

    def create_layout(self):
        main_layout = QtWidgets.QHBoxLayout(self)

        main_layout.addStretch()

        cam_thresh_layout = QtWidgets.QVBoxLayout()

        render_cam_layout = QtWidgets.QHBoxLayout()
        render_cam_layout.addStretch()
        render_cam_layout.addWidget(self.render_cam_lbl)
        render_cam_layout.addWidget(self.render_cam_cmbx)

        threshold_layout = QtWidgets.QHBoxLayout()
        threshold_layout.addStretch()
        threshold_layout.addWidget(self.threshold_lbl)
        threshold_layout.addWidget(self.threshold_le)

        cam_thresh_layout.addLayout(render_cam_layout)
        cam_thresh_layout.addLayout(threshold_layout)

        main_layout.addStretch()
        main_layout.addLayout(cam_thresh_layout)
        main_layout.addWidget(MWidgets.QVLine())

        res_layout = QtWidgets.QHBoxLayout()

        res_inputs_layout = QtWidgets.QVBoxLayout()

        res_x_layout = QtWidgets.QHBoxLayout()
        res_x_layout.addStretch()
        res_x_layout.addWidget(self.res_x_lbl)
        res_x_layout.addWidget(self.res_x_le)

        res_inputs_layout.addLayout(res_x_layout)

        res_y_layout = QtWidgets.QHBoxLayout()
        res_y_layout.addStretch()
        res_y_layout.addWidget(self.res_y_lbl)
        res_y_layout.addWidget(self.res_y_le)

        res_inputs_layout.addLayout(res_y_layout)

        res_layout.addLayout(res_inputs_layout)
        res_layout.addWidget(self.res_asplock_img_btn)
        # res_layout.addStretch()

        main_layout.addLayout(res_layout)
        main_layout.addWidget(MWidgets.QVLine())

        ovrd_layout = QtWidgets.QVBoxLayout()
        ovrd_layout.addWidget(self.ovrd_displacement_cb)
        ovrd_layout.addWidget(self.ovrd_subdivision_cb)

        main_layout.addLayout(ovrd_layout)

    def set_asp_lock(self):
        current_lock = self.vray_settings.aspectLock.get()

        new_lock = not current_lock

        if current_lock:
            self.res_asplock_img_btn.set_image("F:\\share\\tools\\shelf_icons\\unlinked.png", .75)
        else:
            self.res_asplock_img_btn.set_image("F:\\share\\tools\\shelf_icons\\linked.png", .75)

        self.vray_settings.aspectLock.set(new_lock)

        self.asp_ratio = float(self.vray_settings.width.get()) / float(self.vray_settings.height.get())

    def set_x_res(self):
        try:
            x = float(self.res_x_le.text())
        except Exception:
            self.get_resolution()
            return

        if self.vray_settings.aspectLock.get():
            y = int(float(x) / self.asp_ratio)
            self.vray_settings.height.set(y)
        else:
            y = self.vray_settings.height.get()

        self.vray_settings.width.set(x)

        cmds.setAttr("defaultResolution.width", x)
        cmds.setAttr("defaultResolution.height", y)
        cmds.setAttr("defaultResolution.deviceAspectRatio", (x / y))
        cmds.setAttr("defaultResolution.lockDeviceAspectRatio", 0)
        cmds.setAttr("defaultResolution.pixelAspect", 1.0)

        self.vray_settings.aspectRatio.set(float(x) / float(y))

        self.get_resolution()

    def set_y_res(self):
        try:
            y = float(self.res_y_le.text())
        except Exception:
            self.get_resolution()
            return

        if self.vray_settings.aspectLock.get():
            x = int(float(y) * self.asp_ratio)
            self.vray_settings.width.set(x)
        else:
            x = self.vray_settings.width.get()

        self.vray_settings.height.set(y)

        cmds.setAttr("defaultResolution.width", x)
        cmds.setAttr("defaultResolution.height", y)
        cmds.setAttr("defaultResolution.deviceAspectRatio", (x / y))
        cmds.setAttr("defaultResolution.lockDeviceAspectRatio", 0)
        cmds.setAttr("defaultResolution.pixelAspect", 1.0)

        self.vray_settings.aspectRatio.set(float(x) / float(y))

        self.get_resolution()

    def create_connections(self):
        self.render_cam_cmbx.currentIndexChanged.connect(self.set_render_cam)
        self.res_x_le.editingFinished.connect(self.set_x_res)
        self.res_y_le.editingFinished.connect(self.set_y_res)
        self.threshold_le.editingFinished.connect(self.set_threshold)

        self.ovrd_displacement_cb.stateChanged.connect(
            lambda: self.vray_settings.globopt_geom_displacement.set(self.ovrd_displacement_cb.isChecked()))
        self.ovrd_subdivision_cb.stateChanged.connect(
            lambda: self.vray_settings.globopt_subdivision.set(self.ovrd_subdivision_cb.isChecked()))

        self.res_asplock_img_btn.clicked.connect(self.set_asp_lock)

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

    def set_render_cam(self):
        render_cam = pm.PyNode(self.render_cam_cmbx.currentText())

        for cam in pm.ls(type="camera"):
            if str(cam).replace("Shape", "") == str(render_cam):
                cam.renderable.set(1)
            else:
                cam.renderable.set(0)

    def get_threshold(self):
        if self.vray_settings.samplerType.get() == 4:
            threshold = self.vray_settings.dmcThreshold.get()
        else:
            threshold = self.vray_settings.progressiveThreshold.get()
        self.threshold_le.setText("{:.3f}".format(threshold))

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

    def get_resolution(self):
        settings = pm.PyNode("vraySettings")

        self.res_x_le.setText(str(settings.width.get()))
        self.res_y_le.setText(str(settings.height.get()))

        self.asp_ratio = float(settings.width.get()) / float(settings.height.get())
