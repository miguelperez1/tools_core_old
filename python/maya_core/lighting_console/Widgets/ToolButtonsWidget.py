from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import pymel.core as pm
import vray

from pyqt_commons import MWidgets
from maya_core.material_builder import material_builder_ui

reload(MWidgets)

from maya_core.lighting_console.constants import *


class ToolButtonsWidget(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)
    light_created = QtCore.Signal(str)

    def __init__(self, *args, **kwargs):
        super(ToolButtonsWidget, self).__init__(*args, **kwargs)

        self.setObjectName("ToolButtonsWidget")

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.setContentsMargins(0, 0, 0, 0)

    def create_actions(self):
        pass

    def create_widgets(self):
        icon_scale = .45

        self.render_img_btn = MWidgets.ImagePushButton(100 * icon_scale, 100 * icon_scale)
        self.render_img_btn.set_image("F:\\share\\tools\\shelf_icons\\render.png")
        self.render_img_btn.setToolTip("Render")

        self.focus_light_img_btn = MWidgets.ImagePushButton(100 * icon_scale, 100 * icon_scale)
        self.focus_light_img_btn.set_image("F:\\share\\tools\\shelf_icons\\move_toi.png")
        self.focus_light_img_btn.setToolTip("Move to Camera")

        self.create_shotcam_img_btn = MWidgets.ImagePushButton(100 * icon_scale, 100 * icon_scale)
        self.create_shotcam_img_btn.set_image("F:\\share\\tools\\shelf_icons\\shotcam.png")
        self.create_shotcam_img_btn.setToolTip("Create Shot Cam")

        self.rect_light_img_btn = MWidgets.ImagePushButton(100 * icon_scale, 100 * icon_scale)
        self.rect_light_img_btn.set_image(ICONS["VRayLightRectShape"])
        self.rect_light_img_btn.setToolTip("Create VRay Rect Light")

        self.sphere_light_img_btn = MWidgets.ImagePushButton(100 * icon_scale, 100 * icon_scale)
        self.sphere_light_img_btn.set_image(ICONS["VRayLightSphereShape"])
        self.sphere_light_img_btn.setToolTip("Create VRay Sphere Light")

        self.dome_light_img_btn = MWidgets.ImagePushButton(100 * icon_scale, 100 * icon_scale)
        self.dome_light_img_btn.set_image(ICONS["VRayLightDomeShape"])
        self.dome_light_img_btn.setToolTip("Create VRay Dome Light")

        self.dist_light_img_btn = MWidgets.ImagePushButton(100 * icon_scale, 100 * icon_scale)
        self.dist_light_img_btn.set_image(ICONS["directionalLight"])
        self.dist_light_img_btn.setToolTip("Create Dist Light")

        self.vray_cloud_img_btn = MWidgets.ImagePushButton(100 * icon_scale, 100 * icon_scale)
        self.vray_cloud_img_btn.set_image(
            "C:\\Program Files\\Autodesk\\Maya2020\\vray\\icons\\shelf_cloud_rendering_200.png")
        self.vray_cloud_img_btn.setToolTip("Submit to Chaos Cloud")

        self.light_rig_img_btn = MWidgets.ImagePushButton(100 * icon_scale, 100 * icon_scale)
        self.light_rig_img_btn.set_image("F:\\share\\tools\\shelf_icons\\light_rig.png")
        self.light_rig_img_btn.setToolTip("Create Light Rig")

        self.material_builder_img_btn = MWidgets.ImagePushButton(100 * icon_scale, 100 * icon_scale)
        self.material_builder_img_btn.set_image("F:\\share\\tools\\shelf_icons\\vray3.png")
        self.material_builder_img_btn.setToolTip("Material Builder")

        self.volumebox_img_btn = MWidgets.ImagePushButton(100 * icon_scale, 100 * icon_scale)
        self.volumebox_img_btn.set_image("F:\\share\\tools\\shelf_icons\\volumebox.png")
        self.volumebox_img_btn.setToolTip("Create Volume Box")

    def create_layout(self):
        tools_buttons_layout = QtWidgets.QHBoxLayout(self)
        tools_buttons_layout.setSpacing(GLOBAL_SPACING)

        tools_buttons_layout.addWidget(self.render_img_btn)
        tools_buttons_layout.addWidget(MWidgets.QVLine())
        tools_buttons_layout.addWidget(self.focus_light_img_btn)
        tools_buttons_layout.addWidget(MWidgets.QVLine())
        tools_buttons_layout.addWidget(self.material_builder_img_btn)
        tools_buttons_layout.addWidget(MWidgets.QVLine())
        tools_buttons_layout.addWidget(self.volumebox_img_btn)
        tools_buttons_layout.addWidget(MWidgets.QVLine())
        tools_buttons_layout.addWidget(self.rect_light_img_btn)
        tools_buttons_layout.addWidget(self.sphere_light_img_btn)
        tools_buttons_layout.addWidget(self.dome_light_img_btn)
        tools_buttons_layout.addWidget(self.dist_light_img_btn)
        tools_buttons_layout.addWidget(MWidgets.QVLine())
        tools_buttons_layout.addWidget(self.vray_cloud_img_btn)
        tools_buttons_layout.addStretch()

    def create_connections(self):
        self.render_img_btn.clicked.connect(self.render_img_btn_callback)
        self.create_shotcam_img_btn.clicked.connect(self.create_shotcam_img_btn_callback)
        self.focus_light_img_btn.clicked.connect(self.focus_light_img_btn_callback)
        self.light_rig_img_btn.clicked.connect(self.light_rig_img_btn_callback)
        self.material_builder_img_btn.clicked.connect(self.material_builder_img_btn_callback)
        self.volumebox_img_btn.clicked.connect(self.volumebox_img_btn_callback)
        self.rect_light_img_btn.clicked.connect(self.rect_light_img_btn_callback)
        self.sphere_light_img_btn.clicked.connect(self.sphere_light_img_btn_callback)
        self.dome_light_img_btn.clicked.connect(self.dome_light_img_btn_callback)
        self.dist_light_img_btn.clicked.connect(self.dist_light_img_btn_callback)
        self.vray_cloud_img_btn.clicked.connect(self.vray_cloud_img_btn_callback)

    def render_img_btn_callback(self):
        # self.log.result("Rendering")
        for cam in pm.ls(type="camera"):
            cam = pm.PyNode(cam.replace("Shape", ""))
            if cam.renderable.get():
                render_cam = cam
                break

        pm.vrend(camera=render_cam)

    def create_shotcam_img_btn_callback(self):
        cameraName = cmds.camera()
        camera = cmds.rename(cameraName[0], 'shotCAM')
        cmds.setAttr('{}.displayGateMaskOpacity'.format(camera), 1)
        cmds.setAttr('{}.displayGateMaskColor'.format(camera), 0, 0, 0, type='double3')
        cmds.setAttr('{}.focalLength'.format(camera), 50)
        cmds.setAttr("{}.displayFilmGate".format(camera), 1)
        cmds.setAttr("{}.displayResolution".format(camera), 1)
        # self.log.result("Created shotCam")

    def focus_light_img_btn_callback(self):
        pass
        # self.log.info("TODO: focus_light_img_btn_callback")

    def light_rig_img_btn_callback(self):
        if cmds.objExists("l_rig"):
            self.log_event.emit("warning", "light rig already exists, skipping")
            return

        cmds.group(n="l_rig", em=True)
        self.log_event.emit("result", "created empty light rig")

    def material_builder_img_btn_callback(self):
        material_builder_ui.main()

    def rect_light_img_btn_callback(self):
        trans = cmds.createNode('transform', n='l_rect')
        lgt = cmds.shadingNode('VRayLightRectShape', n=trans + "Shape", p=trans, asLight=True)

        light_node = pm.PyNode(lgt)

        light_node.intensity.set(1)
        light_node.invisible.set(1)

        self.light_created.emit(lgt)

    def sphere_light_img_btn_callback(self):
        trans = cmds.createNode('transform', n='l_sphere')
        lgt = cmds.shadingNode('VRayLightSphereShape', n=trans + "Shape", p=trans, asLight=True)
        lgt_shape = cmds.listRelatives(lgt, shapes=True)[0]

        lgt_node = pm.PyNode(lgt)

        lgt_node.intensity.set(1)
        lgt_node.invisible.set(1)

        self.light_created.emit(lgt)

    def dome_light_img_btn_callback(self):
        trans = cmds.createNode('transform', n='l_dome')
        lgt = cmds.shadingNode('VRayLightDomeShape', n=trans + "Shape", p=trans, asLight=True)
        lgt_node = pm.PyNode(lgt)

        lgt_node.intensity.set(1)
        lgt_node.invisible.set(1)

        self.light_created.emit(lgt)

    def dist_light_img_btn_callback(self):
        trans = cmds.createNode('transform', n='l_directional')
        lgt = cmds.shadingNode('directionalLight', n=trans + "Shape", p=trans, asLight=True)

        lgt_node = pm.PyNode(lgt)

        lgt_node.intensity.set(1)
        lgt_node.lightAngle.set(3)

        self.light_created.emit(lgt)

    def vray_cloud_img_btn_callback(self):
        vray.vray_cloud_rendering.vrayCreateCloudSettingsWindow()

    def volumebox_img_btn_callback(self):
        pass
        # self.log.info("TODO: volumebox_img_btn_callback")
