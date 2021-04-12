from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import maya.cmds as cmds
import pymel.core as pm
import vray

from pyqt_commons import MWidgets
from maya_core.asset_builder import asset_builder_ui
from maya_core.asset_manager.asset_browser import asset_browser_ui
from maya_core.common_tools.logger import Logger

import inspect

reload(MWidgets)

import os
import sys
import subprocess

log = Logger()
log.status = True


def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class LightingConsole(QtWidgets.QMainWindow):
    """
    Dialog used to demonstrates many of the standard dialogs available in Qt
    """

    def __init__(self, parent=maya_main_window()):
        super(LightingConsole, self).__init__(parent)

        self.setWindowTitle("Lighting Console")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        scale = 1.1
        self.res_x = 1920 * scale
        self.res_y = 1080 * scale

        self.setFixedSize(self.res_x, self.res_y)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.create_menu()

    def create_actions(self):
        # Render Layers Actions
        self.rl_remove_action = QtWidgets.QAction("Remove")
        self.rl_duplicate_action = QtWidgets.QAction("Duplicate")
        self.rl_add_to_layer_action = QtWidgets.QAction("Add selected to layer")
        self.rl_remove_from_layer_action = QtWidgets.QAction("Remove from layer")
        self.rl_add_layer_action = QtWidgets.QAction("Add Layer")
        self.rl_refresh_action = QtWidgets.QAction("Refresh Layers")

    def create_widgets(self):
        # Render Layers
        self.render_layers_header_lbl = MWidgets.HeaderLabel("Render Layers")

        self.render_layers_tw = QtWidgets.QTreeWidget()
        self.render_layers_tw.setHeaderHidden(True)
        self.render_layers_tw.setFixedHeight(self.res_y * .215)
        self.render_layers_tw.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.render_layers_tw.customContextMenuRequested.connect(self.show_rl_context_menu)

        self.update_render_layers()

        self.render_layer_add_btn = QtWidgets.QPushButton("+")
        self.render_layer_add_btn.setFixedSize(30, 30)

        self.render_layer_remove_btn = QtWidgets.QPushButton("-")
        self.render_layer_remove_btn.setFixedSize(30, 30)

        self.render_layer_refresh_btn = MWidgets.ImagePushButton(30, 30)
        self.render_layer_refresh_btn.set_image("F:\\share\\tools\\shelf_icons\\refresh.png")
        self.render_layer_refresh_btn.setFixedSize(30, 30)

        self.render_layers_btn_wdgt = QtWidgets.QWidget()

        render_layers_btn_layout = QtWidgets.QHBoxLayout(self.render_layers_btn_wdgt)
        render_layers_btn_layout.addStretch()
        render_layers_btn_layout.addWidget(self.render_layer_refresh_btn)
        render_layers_btn_layout.addWidget(self.render_layer_add_btn)
        render_layers_btn_layout.addWidget(self.render_layer_remove_btn)

        self.render_layers_wdgt = QtWidgets.QWidget()
        self.render_layers_wdgt.setFixedHeight(self.res_y * .3)

        render_layers_layout = QtWidgets.QVBoxLayout(self.render_layers_wdgt)

        render_layers_layout.addWidget(self.render_layers_header_lbl)
        render_layers_layout.addWidget(self.render_layers_tw)
        render_layers_layout.addStretch()
        render_layers_layout.addWidget(self.render_layers_btn_wdgt)
        render_layers_layout.addStretch()

        # Create
        self.create_header_lbl = MWidgets.HeaderLabel("Create")

        self.create_tw = QtWidgets.QTreeWidget()
        self.create_tw.setFixedWidth(self.res_x / 6)
        self.create_tw.setHeaderHidden(True)

        self.create_types = ["Lights", "Modifiers", "Volumes", "Other"]

        self.create_search_lbl = QtWidgets.QLabel("Search: ")
        self.create_search_le = QtWidgets.QLineEdit()

        for create_type in self.create_types:
            create_item = QtWidgets.QTreeWidgetItem()
            create_item.setSizeHint(0, QtCore.QSize(100, 30))
            create_item.setText(0, create_type)
            create_item.setChildIndicatorPolicy(QtWidgets.QTreeWidgetItem.ShowIndicator)

            self.create_tw.addTopLevelItem(create_item)

        # Console
        self.console_header_lbl = MWidgets.HeaderLabel("Console")

        self.console_tw = QtWidgets.QTreeWidget()
        self.console_tw.setFixedSize(self.res_x / 2, self.res_y * .675)
        self.console_tw.setHeaderHidden(True)

        self.console_wdgt = QtWidgets.QWidget()

        console_layout = QtWidgets.QVBoxLayout(self.console_wdgt)
        console_layout.addWidget(self.console_header_lbl)
        console_layout.addWidget(self.console_tw)

        # AOVs
        self.aovs_tw = QtWidgets.QTreeWidget()
        self.aovs_tw.setFixedSize(self.res_x / 2, self.res_y * .2)

        aovs_tw_header = QtWidgets.QTreeWidgetItem()
        aovs_tw_header.setText(0, "AOVs")
        self.aovs_tw.setHeaderItem(aovs_tw_header)

        # Properties
        self.properties_header_lbl = MWidgets.HeaderLabel("Properties")

        self.tmp_info_lbl = QtWidgets.QLabel()
        self.tmp_info_lbl.setText("Lights: color, intensity/exp, temp, tex, directional"
                                  "Render Layer")

        # Tool Buttons
        icon_scale = .55

        self.asset_browser_img_btn = MWidgets.ImagePushButton(192 * icon_scale, 108 * icon_scale)
        self.asset_browser_img_btn.set_image("F:\\share\\tools\\shelf_icons\\asset_browser.png")
        self.asset_browser_img_btn.setToolTip("Asset Browser")

        self.asset_builder_img_btn = MWidgets.ImagePushButton(192 * icon_scale, 108 * icon_scale)
        self.asset_builder_img_btn.set_image("F:\\share\\tools\\shelf_icons\\asset_builder.png")
        self.asset_builder_img_btn.setToolTip("Asset Builder")

        self.render_img_btn = MWidgets.ImagePushButton(100 * icon_scale, 100 * icon_scale)
        self.render_img_btn.set_image("F:\\share\\tools\\shelf_icons\\render.png")
        self.render_img_btn.setToolTip("Render")

        self.render_ipr_img_btn = MWidgets.ImagePushButton(100 * icon_scale, 100 * icon_scale)
        self.render_ipr_img_btn.set_image("F:\\share\\tools\\shelf_icons\\ipr.png")
        self.render_ipr_img_btn.setToolTip("IPR Render")

        self.focus_light_img_btn = MWidgets.ImagePushButton(100 * icon_scale, 100 * icon_scale)
        self.focus_light_img_btn.set_image("F:\\share\\tools\\shelf_icons\\move_toi.png")
        self.focus_light_img_btn.setToolTip("Move to Camera")

        self.create_shotcam_img_btn = MWidgets.ImagePushButton(100 * icon_scale, 100 * icon_scale)
        self.create_shotcam_img_btn.set_image("F:\\share\\tools\\shelf_icons\\shotcam.png")
        self.create_shotcam_img_btn.setToolTip("Create Shot Cam")

        self.rect_light_img_btn = MWidgets.ImagePushButton(100 * icon_scale, 100 * icon_scale)
        self.rect_light_img_btn.set_image("C:\\Program Files\\Autodesk\\Maya2020\\vray\\icons\\shelf_LightRect_200.png")
        self.rect_light_img_btn.setToolTip("Create VRay Rect Light")

        self.sphere_light_img_btn = MWidgets.ImagePushButton(100 * icon_scale, 100 * icon_scale)
        self.sphere_light_img_btn.set_image(
            "C:\\Program Files\\Autodesk\\Maya2020\\vray\\icons\\shelf_LightSphere_200.png")
        self.sphere_light_img_btn.setToolTip("Create VRay Sphere Light")

        self.dome_light_img_btn = MWidgets.ImagePushButton(100 * icon_scale, 100 * icon_scale)
        self.dome_light_img_btn.set_image("C:\\Program Files\\Autodesk\\Maya2020\\vray\\icons\\shelf_LightDome_200.png")
        self.dome_light_img_btn.setToolTip("Create VRay Dome Light")

        self.dist_light_img_btn = MWidgets.ImagePushButton(100 * icon_scale, 100 * icon_scale)
        self.dist_light_img_btn.set_image(":/directionallight.png")
        self.dome_light_img_btn.setToolTip("Create Dist Light")

        self.gobo_img_btn = MWidgets.ImagePushButton(100 * icon_scale, 100 * icon_scale)
        self.gobo_img_btn.set_image("F:\\share\\tools\\shelf_icons\\gobo.png")
        self.gobo_img_btn.setToolTip("Create Gobo")

        self.vray_cloud_img_btn = MWidgets.ImagePushButton(100 * icon_scale, 100 * icon_scale)
        self.vray_cloud_img_btn.set_image(
            "C:\\Program Files\\Autodesk\\Maya2020\\vray\\icons\\shelf_cloud_rendering_200.png")
        self.vray_cloud_img_btn.setToolTip("Submit to Chaos Cloud")

        self.light_rig_img_btn = MWidgets.ImagePushButton(100 * icon_scale, 100 * icon_scale)
        self.light_rig_img_btn.set_image("F:\\share\\tools\\shelf_icons\\light_rig.png")
        self.light_rig_img_btn.setToolTip("Create Light Rig")

    def create_layout(self):
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)

        header_btns_layout = QtWidgets.QHBoxLayout()
        header_btns_layout.addWidget(self.render_img_btn)
        # header_btns_layout.addWidget(self.render_ipr_img_btn)
        header_btns_layout.addWidget(MWidgets.QVLine())
        header_btns_layout.addWidget(self.create_shotcam_img_btn)
        header_btns_layout.addWidget(self.focus_light_img_btn)
        header_btns_layout.addWidget(MWidgets.QVLine())
        header_btns_layout.addWidget(self.light_rig_img_btn)
        header_btns_layout.addWidget(MWidgets.QVLine())
        header_btns_layout.addWidget(self.asset_browser_img_btn)
        # header_btns_layout.addWidget(self.asset_builder_img_btn)
        header_btns_layout.addWidget(MWidgets.QVLine())
        header_btns_layout.addWidget(self.rect_light_img_btn)
        header_btns_layout.addWidget(self.sphere_light_img_btn)
        header_btns_layout.addWidget(self.dome_light_img_btn)
        header_btns_layout.addWidget(self.dist_light_img_btn)
        header_btns_layout.addWidget(self.gobo_img_btn)
        header_btns_layout.addWidget(MWidgets.QVLine())
        header_btns_layout.addWidget(self.vray_cloud_img_btn)
        header_btns_layout.addStretch()

        col_layout = QtWidgets.QHBoxLayout()

        col_1_layout = QtWidgets.QVBoxLayout()
        col_1_layout.addWidget(self.render_layers_wdgt)
        col_1_layout.addWidget(MWidgets.QHLine())
        col_1_layout.addWidget(self.create_header_lbl)
        col_1_layout.addWidget(self.create_search_le)
        col_1_layout.addWidget(self.create_tw)

        col_2_layout = QtWidgets.QVBoxLayout()
        col_2_layout.addWidget(self.console_wdgt)
        col_2_layout.addWidget(self.aovs_tw)

        col_3_layout = QtWidgets.QVBoxLayout()
        col_3_layout.addWidget(self.properties_header_lbl)
        col_3_layout.addWidget(self.tmp_info_lbl)
        col_3_layout.addStretch()

        col_layout.addLayout(col_1_layout)
        col_layout.addLayout(col_2_layout)
        col_layout.addLayout(col_3_layout)
        col_layout.addStretch()

        main_layout.addLayout(header_btns_layout)
        main_layout.addWidget(MWidgets.QHLine())
        main_layout.addLayout(col_layout)

    def create_connections(self):
        # BTNs
        self.render_img_btn.clicked.connect(self.render_img_btn_callback)
        self.render_ipr_img_btn.clicked.connect(self.render_ipr_img_btn_callback)
        self.create_shotcam_img_btn.clicked.connect(self.create_shotcam_img_btn_callback)
        self.focus_light_img_btn.clicked.connect(self.focus_light_img_btn_callback)
        self.light_rig_img_btn.clicked.connect(self.light_rig_img_btn_callback)
        self.asset_browser_img_btn.clicked.connect(self.asset_browser_img_btn_callback)
        self.asset_builder_img_btn.clicked.connect(self.asset_builder_img_btn_callback)
        self.rect_light_img_btn.clicked.connect(self.rect_light_img_btn_callback)
        self.sphere_light_img_btn.clicked.connect(self.sphere_light_img_btn_callback)
        self.dome_light_img_btn.clicked.connect(self.dome_light_img_btn_callback)
        self.dist_light_img_btn.clicked.connect(self.dist_light_img_btn_callback)
        self.gobo_img_btn.clicked.connect(self.gobo_img_btn_callback)
        self.vray_cloud_img_btn.clicked.connect(self.vray_cloud_img_btn_callback)

        # Render Layers
        self.rl_remove_action.triggered.connect(self.rl_remove_action_callback)
        self.rl_duplicate_action.triggered.connect(self.rl_duplicate_action_callback)
        self.rl_add_to_layer_action.triggered.connect(self.rl_add_to_layer_action_callback)
        self.rl_remove_from_layer_action.triggered.connect(self.rl_remove_from_layer_action_callback)
        self.rl_add_layer_action.triggered.connect(self.rl_add_layer_action_callback)
        self.rl_refresh_action.triggered.connect(self.rl_refresh_action_callback)
        self.render_layer_add_btn.clicked.connect(self.render_layer_add_btn_callback)
        self.render_layer_remove_btn.clicked.connect(self.render_layer_remove_btn_callback)
        self.render_layer_refresh_btn.clicked.connect(self.render_layer_refresh_btn_callback)

    def create_menu(self):
        self.menu_bar = QtWidgets.QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        file_menu = QtWidgets.QMenu("File", self)
        edit_menu = QtWidgets.QMenu("Edit", self)
        tools_menu = QtWidgets.QMenu("Tools", self)
        help_menu = QtWidgets.QMenu("Help", self)

        self.menu_bar.addMenu(file_menu)
        self.menu_bar.addMenu(edit_menu)
        self.menu_bar.addMenu(tools_menu)
        self.menu_bar.addMenu(help_menu)

    def show_rl_context_menu(self, eventPosition):
        child = self.childAt(self.sender().mapTo(self, eventPosition))
        item = self.render_layers_tw.itemAt(eventPosition)

        contextMenu = QtWidgets.QMenu(self)

        if item is None:
            contextMenu.addAction(self.rl_add_layer_action)
        else:
            about_action = QtWidgets.QAction(item.text(0))

            contextMenu.addAction(about_action)
            contextMenu.addSeparator()
            contextMenu.addAction(self.rl_remove_action)
            contextMenu.addAction(self.rl_duplicate_action)
            contextMenu.addSeparator()
            contextMenu.addAction(self.rl_add_to_layer_action)
            contextMenu.addAction(self.rl_remove_from_layer_action)

        contextMenu.addSeparator()
        contextMenu.addAction(self.rl_refresh_action)

        action = contextMenu.exec_(child.mapToGlobal(eventPosition))

    def render_img_btn_callback(self):
        log.info("TODO: render_img_btn_callback")

        pm.vrend()

    def render_ipr_img_btn_callback(self):
        log.info("TODO: render_ipr_img_btn_callback")

    def create_shotcam_img_btn_callback(self):
        cameraName = cmds.camera()
        camera = cmds.rename(cameraName[0], 'shotCAM')
        cmds.setAttr('{}.displayGateMaskOpacity'.format(camera), 1)
        cmds.setAttr('{}.displayGateMaskColor'.format(camera), 0, 0, 0, type='double3')
        cmds.setAttr('{}.focalLength'.format(camera), 50)
        cmds.setAttr("{}.displayFilmGate".format(camera), 1)
        cmds.setAttr("{}.displayResolution".format(camera), 1)

    def focus_light_img_btn_callback(self):
        log.info("TODO: focus_light_img_btn_callback")

    def light_rig_img_btn_callback(self):
        log.info("TODO: light_rig_img_btn_callback")

    def asset_browser_img_btn_callback(self):
        reload(asset_browser_ui)

    def asset_builder_img_btn_callback(self):
        reload(asset_builder_ui)

    def rect_light_img_btn_callback(self):
        log.info("TODO: rect_light_img_btn_callback")

    def sphere_light_img_btn_callback(self):
        log.info("TODO: sphere_light_img_btn_callback")

    def dome_light_img_btn_callback(self):
        log.info("TODO: dome_light_img_btn_callback")

    def dist_light_img_btn_callback(self):
        log.info("TODO: dist_light_img_btn_callback")

    def gobo_img_btn_callback(self):
        log.info("TODO: gobo_img_btn_callback")

    def vray_cloud_img_btn_callback(self):
        vray.vray_cloud_rendering.vrayCreateCloudSettingsWindow()

    def rl_remove_action_callback(self):
        log.info("TODO: rl_remove_action_callback")

    def rl_duplicate_action_callback(self):
        log.info("TODO: rl_duplicate_action_callback")

    def rl_add_to_layer_action_callback(self):
        log.info("TODO: rl_add_to_layer_action_callback")

    def rl_remove_from_layer_action_callback(self):
        log.info("TODO: rl_remove_from_layer_action_callback")

    def rl_add_layer_action_callback(self):
        log.info("TODO: rl_add_layer_action_callback")

    def rl_refresh_action_callback(self):
        log.info("TODO: rl_refresh_layer_action_callback")

    def render_layer_add_btn_callback(self):
        log.info("TODO: render_layer_add_btn_callback")

    def render_layer_remove_btn_callback(self):
        log.info("TODO: render_layer_remove_btn_callback")

    def render_layer_refresh_btn_callback(self):
        self.update_render_layers()

    def update_render_layers(self):
        self.render_layers_tw.clear()

        renderlayers = cmds.ls(type="renderLayer")

        if "defaultRenderLayer" in renderlayers:
            renderlayers.remove("defaultRenderLayer")
            renderlayers.append("masterLayer")

        for render_layer in renderlayers:
            render_layer_item = QtWidgets.QTreeWidgetItem()
            render_layer_item.setText(0, render_layer)
            render_layer_item.setFlags(render_layer_item.flags() | QtCore.Qt.ItemIsEditable)

            self.render_layers_tw.addTopLevelItem(render_layer_item)

            current_render_layer = cmds.editRenderLayerGlobals(query=True, currentRenderLayer=True)

            if render_layer == current_render_layer or (
                    render_layer == "masterLayer" and current_render_layer == "defaultRenderLayer"):
                render_layer_item.setSelected(True)


if __name__ == "__main__" or __name__ == "maya_core.render_manager.render_manager_ui":

    try:
        dialog.close()
        dialog.deleteLater()
    except:
        pass

    dialog = LightingConsole()
    dialog.show()
