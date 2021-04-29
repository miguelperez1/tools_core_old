from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import maya.cmds as cmds
import pymel.core as pm
import vray

from pyqt_commons import MWidgets
from maya_core.asset_manager.asset_browser import AssetBrowser
from maya_core.common_tools.logger import Logger
from maya_core.material_builder import material_builder_ui

reload(MWidgets)
reload(AssetBrowser)


def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class LightConsoleLogger(object):
    def __init__(self):
        self.log = Logger()
        self.log.status = True

        self.log_le = QtWidgets.QLineEdit()
        self.log_le.setEnabled(False)

    def info(self, message):
        self.log_le.setStyleSheet("color: rgb(135, 203, 203);")
        self.log_le.setText(self.log.info(message))

    def warning(self, message):
        self.log_le.setStyleSheet("color: rgb(223, 229, 39);")
        self.log_le.setText(self.log.warning(message))

    def error(self, message):
        self.log_le.setStyleSheet("color: rgb(244, 40, 40);")
        self.log_le.setText(self.log.error(message))

    def result(self, message):
        self.log_le.setStyleSheet("color: rgb(42, 180, 34);")
        self.log_le.setText(self.log.result(message))


class LightConsoleItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, light_type, *args, **kwargs):
        super(LightConsoleItem, self).__init__(*args, **kwargs)

        self.light_type = light_type

        self.l_rig = False
        if cmds.objExists("l_rig"):
            self.l_rig = True

        self.setSizeHint(0, QtCore.QSize(50, 50))

        self.create_light()

    def create_light(self):
        self.light_trans = cmds.createNode('transform', n=self.light_type.split("Shape")[0])

        self.light = cmds.shadingNode(self.light_type, n=self.light_type, asLight=True, p=self.light_trans)

        self.setData(0, QtCore.Qt.UserRole, self.light)

        self.setText(2, self.light.split(""))

        if self.light.startswith("VRay"):
            intensity = cmds.getAttr("{}.intensity".format(self.light))
            self.setText(3, str(intensity))

        if cmds.objExists("l_rig"):
            cmds.parent(self.light_trans, "l_rig")


class LightingConsole(QtWidgets.QMainWindow):
    def __init__(self, parent=maya_main_window()):
        super(LightingConsole, self).__init__(parent)
        self.version = "1.0.0"

        self.setWindowTitle("Lighting Console")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.log = LightConsoleLogger()
        self.log.result("Loaded Lighting Console version-" + self.version)

        self.scale = 1
        self.res_x = 2400 * self.scale
        self.res_y = 1320 * self.scale

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

        self.add_set_action = QtWidgets.QAction("Add Set")
        self.remove_set_action = QtWidgets.QAction("Remove Set")
        self.duplicate_set_action = QtWidgets.QAction("Duplicate Set")
        self.add_to_set_action = QtWidgets.QAction("Add selected to set")
        self.remove_from_set_action = QtWidgets.QAction("Remove from set")
        self.refresh_sets_action = QtWidgets.QAction("Refresh Sets")

    def create_widgets(self):
        # Tool Buttons
        icon_scale = .50

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

        # Render Layers
        self.render_layers_header_lbl = MWidgets.HeaderLabel("Render Layers")

        self.render_layers_tw = QtWidgets.QTreeWidget()
        self.render_layers_tw.setHeaderHidden(True)
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

        self.render_layer_duplicate_btn = MWidgets.ImagePushButton(30, 30)
        self.render_layer_duplicate_btn.set_image("F:\\share\\tools\\shelf_icons\\duplicate.png")
        self.render_layer_duplicate_btn.setFixedSize(30, 30)

        # Create Nodes
        self.create_header_lbl = MWidgets.HeaderLabel("Create")
        self.create_add_btn = QtWidgets.QPushButton("+")
        self.create_add_btn.setFixedSize(30, 30)

        self.create_tw = QtWidgets.QTreeWidget()
        self.create_tw.setHeaderHidden(True)

        self.create_search_lbl = QtWidgets.QLabel("Search: ")
        self.create_search_le = QtWidgets.QLineEdit()

        self.create_create_widgets()
        self.create_tw.setAlternatingRowColors(True)

        # Console
        self.console_header_lbl = MWidgets.HeaderLabel("Console")

        self.console_tw = QtWidgets.QTreeWidget()
        self.console_tw.setAlternatingRowColors(True)
        self.console_tw.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        console_tw_header_item = QtWidgets.QTreeWidgetItem(
            ["Enabled", "", "Name", "Exposure", "Color", 'Temperature', "Tex", "Directional", 'Invisible'])

        self.console_tw.setHeaderItem(console_tw_header_item)

        self.console_tw.setColumnWidth(0, 100)
        self.console_tw.setColumnWidth(2, 250)
        self.console_tw.setColumnWidth(3, 100)
        self.console_tw.resizeColumnToContents(1)

        # Asset Browser
        self.asset_browser_wdgt = AssetBrowser.AssetBrowser(1.95, 7, libraries=['hdri', 'studio_lights', 'gobo_lights',
                                                                                'clouds'])

        # Properties
        self.properties_header_lbl = MWidgets.HeaderLabel("Properties")

        self.tmp_info_lbl = QtWidgets.QLabel()
        self.tmp_info_lbl.setText("Lights: color, intensity/exp, temp, tex, directional"
                                  "Render Layer")

        # Sets
        self.sets_header_lbl = MWidgets.HeaderLabel("Sets")
        self.sets_tw = QtWidgets.QTreeWidget()
        sets_tw_header_item = QtWidgets.QTreeWidgetItem(['Sets'])
        self.sets_tw.setHeaderItem(sets_tw_header_item)

        self.set_members_tw = QtWidgets.QTreeWidget()
        set_members_tw_header_item = QtWidgets.QTreeWidgetItem(['Set Members'])
        self.set_members_tw.setHeaderItem(set_members_tw_header_item)

        self.add_set_btn = QtWidgets.QPushButton("+")
        self.add_set_btn.setFixedSize(30, 30)

        self.remove_set_btn = QtWidgets.QPushButton("-")
        self.remove_set_btn.setFixedSize(30, 30)

        self.sets_refresh_btn = MWidgets.ImagePushButton(30, 30)
        self.sets_refresh_btn.set_image("F:\\share\\tools\\shelf_icons\\refresh.png")
        self.sets_refresh_btn.setFixedSize(30, 30)

        self.sets_duplicate_btn = MWidgets.ImagePushButton(30, 30)
        self.sets_duplicate_btn.set_image("F:\\share\\tools\\shelf_icons\\duplicate.png")
        self.sets_duplicate_btn.setFixedSize(30, 30)

        self.sets_tw.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.sets_tw.customContextMenuRequested.connect(self.show_sets_tw_context_menu)

        self.set_members_tw.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.set_members_tw.customContextMenuRequested.connect(self.show_set_members_tw_context_menu)

        self.update_sets()

        self.create_central_widgets()

    def create_central_widgets(self):
        # Create Main Section Widgets

        # MAIN SECTION (2200, 1500)
        # Row 1 (2100, 75)
        #   Col 1 (2100, 75)
        #   - Tool Buttons (2100, 100)
        # Row 2 (2100, 1200)
        #   Col 1 (300, 1200)
        #   - Render Layers (300, 400)
        #   - Create Nodes (300, 900)
        #   Col 2 (1275, 1200)
        #   - Console (1275, 900)
        #   - Asset Browser (1050, 300)
        #   Col 3 (525, 1200)
        #   - Properties (525, ?)
        #   - Sets (525, ?)

        # Tool Buttons
        self.tool_buttons_cw = QtWidgets.QWidget()
        self.tool_buttons_cw.setMinimumSize(self.res_x, self.res_y * .05)

        tools_buttons_layout = QtWidgets.QHBoxLayout(self.tool_buttons_cw)

        tools_buttons_layout.addWidget(self.render_img_btn)
        tools_buttons_layout.addWidget(MWidgets.QVLine())
        tools_buttons_layout.addWidget(self.create_shotcam_img_btn)
        tools_buttons_layout.addWidget(self.focus_light_img_btn)
        tools_buttons_layout.addWidget(MWidgets.QVLine())
        tools_buttons_layout.addWidget(self.light_rig_img_btn)
        tools_buttons_layout.addWidget(self.material_builder_img_btn)
        tools_buttons_layout.addWidget(MWidgets.QVLine())
        tools_buttons_layout.addWidget(self.rect_light_img_btn)
        tools_buttons_layout.addWidget(self.sphere_light_img_btn)
        tools_buttons_layout.addWidget(self.dome_light_img_btn)
        tools_buttons_layout.addWidget(self.dist_light_img_btn)
        tools_buttons_layout.addWidget(MWidgets.QVLine())
        tools_buttons_layout.addWidget(self.vray_cloud_img_btn)
        tools_buttons_layout.addStretch()

        # Render Layers
        self.render_layers_cw = QtWidgets.QWidget()
        self.render_layers_cw.setMinimumWidth(self.res_x * .14)
        self.render_layers_cw.setMaximumHeight(self.res_y * .25)

        render_layers_layout = QtWidgets.QVBoxLayout(self.render_layers_cw)

        render_layers_layout.addWidget(self.render_layers_header_lbl)
        render_layers_layout.addWidget(self.render_layers_tw)

        render_layers_btn_layout = QtWidgets.QHBoxLayout()
        render_layers_btn_layout.addStretch()
        render_layers_btn_layout.addWidget(self.render_layer_refresh_btn)
        render_layers_btn_layout.addWidget(self.render_layer_add_btn)
        render_layers_btn_layout.addWidget(self.render_layer_remove_btn)
        render_layers_btn_layout.addWidget(self.render_layer_duplicate_btn)

        render_layers_layout.addLayout(render_layers_btn_layout)

        # Create Nodes
        self.create_cw = QtWidgets.QWidget()
        self.create_cw.setMinimumWidth(self.res_x * .14)

        create_layout = QtWidgets.QVBoxLayout(self.create_cw)

        create_header_layout = QtWidgets.QHBoxLayout()
        create_header_layout.addWidget(self.create_header_lbl)
        create_header_layout.addStretch()
        create_header_layout.addWidget(self.create_add_btn)

        create_layout.addLayout(create_header_layout)
        create_layout.addWidget(self.create_search_le)
        create_layout.addWidget(self.create_tw)

        # Console
        self.console_cw = QtWidgets.QWidget()
        self.console_cw.setMinimumSize(self.res_x * .65, self.res_y * .53)

        console_layout = QtWidgets.QVBoxLayout(self.console_cw)

        console_layout.addWidget(self.console_header_lbl)
        console_layout.addWidget(self.console_tw)

        # Asset Browser
        self.asset_browser_cw = QtWidgets.QWidget()
        self.asset_browser_cw.setMinimumWidth(self.res_x * .65)

        asset_browser_layout = QtWidgets.QVBoxLayout(self.asset_browser_cw)

        asset_browser_layout.addWidget(self.asset_browser_wdgt)

        # Properties
        self.properties_cw = QtWidgets.QWidget()
        self.properties_cw.setMinimumSize(self.res_x * .2, self.res_y * .6)

        properties_layout = QtWidgets.QVBoxLayout(self.properties_cw)

        properties_layout.addWidget(self.properties_header_lbl)
        properties_layout.addStretch()

        # Sets
        self.sets_cw = QtWidgets.QWidget()
        self.sets_cw.setMinimumSize(self.res_x * .2, self.res_y * .3)

        sets_layout = QtWidgets.QVBoxLayout(self.sets_cw)

        sets_btn_layout = QtWidgets.QHBoxLayout()

        sets_btn_layout.addWidget(self.sets_header_lbl)
        sets_btn_layout.addStretch()
        sets_btn_layout.addWidget(self.sets_refresh_btn)
        sets_btn_layout.addWidget(self.add_set_btn)
        sets_btn_layout.addWidget(self.remove_set_btn)
        sets_btn_layout.addWidget(self.sets_duplicate_btn)

        sets_layout.addLayout(sets_btn_layout)

        sets_tw_layout = QtWidgets.QHBoxLayout()
        sets_tw_layout.addWidget(self.sets_tw)
        sets_tw_layout.addWidget(self.set_members_tw)

        sets_layout.addLayout(sets_tw_layout)

        # Log Layout
        self.log_cw = QtWidgets.QWidget()

        log_layout = QtWidgets.QHBoxLayout(self.log_cw)
        log_layout.addWidget(self.log.log_le)

    def create_layout(self):
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)

        main_layout.addWidget(MWidgets.QHLine())
        main_layout.addWidget(self.tool_buttons_cw)
        main_layout.addWidget(MWidgets.QHLine())

        # Col 1 Layout
        col_1_layout = QtWidgets.QVBoxLayout()

        col_1_layout.addWidget(self.render_layers_cw)
        col_1_layout.addWidget(MWidgets.QHLine())
        col_1_layout.addWidget(self.create_cw)

        # Col 2 Layout
        col_2_layout = QtWidgets.QVBoxLayout()

        col_2_layout.addWidget(self.console_cw)
        col_2_layout.addWidget(MWidgets.QHLine())
        col_2_layout.addWidget(self.asset_browser_cw)

        col_2_layout.addStretch()

        # Col 3 Layout
        col_3_layout = QtWidgets.QVBoxLayout()

        col_3_layout.addWidget(self.properties_cw)
        col_3_layout.addWidget(MWidgets.QHLine())
        col_3_layout.addWidget(self.sets_cw)

        col_3_layout.addStretch()

        # Row 2 Layout
        row_2_layout = QtWidgets.QHBoxLayout()

        row_2_layout.addLayout(col_1_layout)
        row_2_layout.addLayout(col_2_layout)
        row_2_layout.addLayout(col_3_layout)

        main_layout.addLayout(row_2_layout)

        # Row 3 Layout
        row_3_layout = QtWidgets.QHBoxLayout()

        row_3_layout.addWidget(self.log_cw)

        main_layout.addWidget(MWidgets.QHLine())
        main_layout.addLayout(row_3_layout)

    def create_connections(self):
        # BTNs
        self.render_img_btn.clicked.connect(self.render_img_btn_callback)
        self.render_ipr_img_btn.clicked.connect(self.render_ipr_img_btn_callback)
        self.create_shotcam_img_btn.clicked.connect(self.create_shotcam_img_btn_callback)
        self.focus_light_img_btn.clicked.connect(self.focus_light_img_btn_callback)
        self.light_rig_img_btn.clicked.connect(self.light_rig_img_btn_callback)
        self.material_builder_img_btn.clicked.connect(self.material_builder_img_btn_callback)
        self.rect_light_img_btn.clicked.connect(self.rect_light_img_btn_callback)
        self.sphere_light_img_btn.clicked.connect(self.sphere_light_img_btn_callback)
        self.dome_light_img_btn.clicked.connect(self.dome_light_img_btn_callback)
        self.dist_light_img_btn.clicked.connect(self.dist_light_img_btn_callback)
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
        self.render_layer_duplicate_btn.clicked.connect(self.rl_duplicate_action_callback)

        self.render_layers_tw.currentItemChanged.connect(self.update_current_rl)
        self.render_layers_tw.itemChanged.connect(self.render_layers_tw_rename_callback)

        # Console
        self.console_tw.currentItemChanged.connect(self.console_tw_item_changed_callback)

        # Sets
        self.add_set_btn.clicked.connect(self.add_set)
        self.remove_set_btn.clicked.connect(self.remove_set)

        self.add_set_action.triggered.connect(self.add_set)
        self.remove_set_action.triggered.connect(self.remove_set)
        self.duplicate_set_action.triggered.connect(self.duplicate_set)
        self.add_to_set_action.triggered.connect(self.add_to_set)
        self.remove_from_set_action.triggered.connect(self.remove_from_set)
        self.refresh_sets_action.triggered.connect(self.update_sets)

        self.sets_tw.currentItemChanged.connect(self.update_current_set)
        self.sets_tw.itemChanged.connect(self.sets_tw_rename_callback)

        self.sets_refresh_btn.clicked.connect(self.update_sets)
        self.sets_duplicate_btn.clicked.connect(self.duplicate_set)

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
        self.current_rl_item = self.render_layers_tw.itemAt(eventPosition)

        contextMenu = QtWidgets.QMenu(self)

        if self.current_rl_item is None:
            contextMenu.addAction(self.rl_add_layer_action)
        else:
            about_action = QtWidgets.QAction(self.current_rl_item.text(0))

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

    def show_sets_tw_context_menu(self, eventPosition):
        child = self.childAt(self.sender().mapTo(self, eventPosition))
        self.current_set_item = self.sets_tw.itemAt(eventPosition)

        contextMenu = QtWidgets.QMenu(self)

        if self.current_set is None:
            contextMenu.addAction(self.add_set_action)
            contextMenu.addAction(self.refresh_sets_action)

        else:
            about_action = QtWidgets.QAction(self.current_set)

            contextMenu.addAction(about_action)
            contextMenu.addSeparator()
            contextMenu.addAction(self.add_set_action)
            contextMenu.addAction(self.remove_set_action)
            contextMenu.addAction(self.duplicate_set_action)
            contextMenu.addSeparator()
            contextMenu.addAction(self.refresh_sets_action)

        action = contextMenu.exec_(child.mapToGlobal(eventPosition))

    def show_set_members_tw_context_menu(self, eventPosition):
        child = self.childAt(self.sender().mapTo(self, eventPosition))
        self.current_set_member_item = self.set_members_tw.itemAt(eventPosition)

        contextMenu = QtWidgets.QMenu(self)

        if self.current_set_member_item is not None:
            about_action = QtWidgets.QAction(self.current_set_member_item.text(0))
            contextMenu.addAction(about_action)
            contextMenu.addSeparator()
            contextMenu.addAction(self.remove_from_set_action)
            contextMenu.addSeparator()

        contextMenu.addAction(self.add_to_set_action)
        contextMenu.addAction(self.refresh_sets_action)

        action = contextMenu.exec_(child.mapToGlobal(eventPosition))

    def render_img_btn_callback(self):
        self.log.result("Rendering")

        pm.vrend()

    def render_ipr_img_btn_callback(self):
        self.log.info("TODO: render_ipr_img_btn_callback")

    def create_shotcam_img_btn_callback(self):
        cameraName = cmds.camera()
        camera = cmds.rename(cameraName[0], 'shotCAM')
        cmds.setAttr('{}.displayGateMaskOpacity'.format(camera), 1)
        cmds.setAttr('{}.displayGateMaskColor'.format(camera), 0, 0, 0, type='double3')
        cmds.setAttr('{}.focalLength'.format(camera), 50)
        cmds.setAttr("{}.displayFilmGate".format(camera), 1)
        cmds.setAttr("{}.displayResolution".format(camera), 1)
        self.log.result("Created shotCam")

    def focus_light_img_btn_callback(self):
        self.log.info("TODO: focus_light_img_btn_callback")

    def light_rig_img_btn_callback(self):
        if cmds.objExists("l_rig"):
            return

        cmds.group(n="l_rig", em=True)

    def material_builder_img_btn_callback(self):
        material_builder_ui.main()

    def rect_light_img_btn_callback(self):
        new_light_item = LightConsoleItem("VRayLightRectShape")

        self.console_tw.addTopLevelItem(new_light_item)

        icon = MWidgets.PreviewLabel()
        icon.setMinimumSize(45 * self.scale, 45 * self.scale)
        icon.set_image("C:\\Program Files\\Autodesk\\Maya2020\\vray\\icons\\shelf_LightRect_200.png", 45)

        cb = QtWidgets.QCheckBox()
        cb.setChecked(True)

        self.console_tw.setItemWidget(new_light_item, 0, cb)
        self.console_tw.setItemWidget(new_light_item, 1, icon)

        self.log.result("Created VRayLightRect")

    def sphere_light_img_btn_callback(self):
        new_light_item = LightConsoleItem("VRayLightSphereShape")

        self.console_tw.addTopLevelItem(new_light_item)

        icon = MWidgets.PreviewLabel()
        icon.setMinimumSize(45 * self.scale, 45 * self.scale)
        icon.set_image("C:\\Program Files\\Autodesk\\Maya2020\\vray\\icons\\shelf_LightSphere_200.png", 45)

        cb = QtWidgets.QCheckBox()
        cb.setChecked(True)

        self.console_tw.setItemWidget(new_light_item, 0, cb)
        self.console_tw.setItemWidget(new_light_item, 1, icon)

        # new_light_item.setSelected(True)

        self.log.result("Created VRayLightSphere")

    def dome_light_img_btn_callback(self):
        new_light_item = LightConsoleItem("VRayLightDomeShape")

        self.console_tw.addTopLevelItem(new_light_item)

        icon = MWidgets.PreviewLabel()
        icon.setMinimumSize(45 * self.scale, 45 * self.scale)
        icon.set_image("C:\\Program Files\\Autodesk\\Maya2020\\vray\\icons\\shelf_LightDome_200.png", 45)

        cb = QtWidgets.QCheckBox()
        cb.setChecked(True)

        self.console_tw.setItemWidget(new_light_item, 0, cb)
        self.console_tw.setItemWidget(new_light_item, 1, icon)

        # new_light_item.setSelected(True)

        self.log.result("Created VRayLightDome")

    def dist_light_img_btn_callback(self):
        new_light_item = LightConsoleItem("directionalLight")

        self.console_tw.addTopLevelItem(new_light_item)

        icon = MWidgets.PreviewLabel()
        icon.setMinimumSize(45 * self.scale, 45 * self.scale)
        icon.set_image(":/directionallight.png", 45)

        cb = QtWidgets.QCheckBox()
        cb.setChecked(True)

        self.console_tw.setItemWidget(new_light_item, 0, cb)
        self.console_tw.setItemWidget(new_light_item, 1, icon)

        # new_light_item.setSelected(True)

        self.log.result("Created directionalLight")

    def vray_cloud_img_btn_callback(self):
        vray.vray_cloud_rendering.vrayCreateCloudSettingsWindow()

    def rl_remove_action_callback(self):
        current_layer = self.current_rl_item.text(0)

        if current_layer == "masterLayer":
            self.log.error("Cannot delete default render layer")
            return

        if cmds.objExists(current_layer):
            if cmds.editRenderLayerGlobals(q=True, crl=True) == current_layer:
                cmds.editRenderLayerGlobals(crl="defaultRenderLayer")

            cmds.delete(current_layer)

            self.log.result("Deleted " + current_layer)

        self.update_render_layers()

    def rl_duplicate_action_callback(self):
        if self.current_rl is None:
            return

        current_rl = self.current_rl

        if self.current_rl == "masterLayer":
            current_rl = "defaultRenderLayer"

        new_rl = cmds.duplicate(current_rl)[0]

        self.log.result("Created " + new_rl)

        self.update_render_layers()

    def rl_add_to_layer_action_callback(self):
        self.log.info("TODO: rl_add_to_layer_action_callback")

    def rl_remove_from_layer_action_callback(self):
        self.log.info("TODO: rl_remove_from_layer_action_callback")

    def rl_add_layer_action_callback(self):
        rl = cmds.createRenderLayer(empty=True)
        self.log.result("Created " + rl)
        self.update_render_layers()

    def rl_refresh_action_callback(self):
        self.log.info("TODO: rl_refresh_layer_action_callback")

    def render_layer_add_btn_callback(self):
        rl = cmds.createRenderLayer(empty=True)
        self.log.result("Created " + rl)
        self.update_render_layers()

    def render_layer_remove_btn_callback(self):
        current_layer = self.render_layers_tw.selectedItems()[0].text(0)

        if current_layer == "masterLayer":
            self.log.error("Cannot delete default render layer")
            return

        if cmds.objExists(current_layer):
            if cmds.editRenderLayerGlobals(q=True, crl=True) == current_layer:
                cmds.editRenderLayerGlobals(crl="defaultRenderLayer")

            cmds.delete(current_layer)

            self.log.result("Deleted " + current_layer)

        self.update_render_layers()

    def render_layer_refresh_btn_callback(self):
        self.update_render_layers()

    def update_current_rl(self, current_item):
        if current_item is None:
            self.current_rl_item = None
            self.current_rl = None
            return

        self.current_rl_item = current_item
        self.current_rl = self.current_rl_item.text(0)

        if self.current_rl == "masterLayer":
            cmds.editRenderLayerGlobals(crl="defaultRenderLayer")
        else:
            cmds.editRenderLayerGlobals(crl=self.current_rl)

    def render_layers_tw_rename_callback(self, item, column):
        prev_rl_name = self.current_rl
        new_rl_name = item.text(0)

        cmds.rename(self.current_rl, new_rl_name)

        self.update_current_set(item)

        self.log.result("Renamed {0} to {1}".format(prev_rl_name, new_rl_name))

    def update_render_layers(self):
        self.render_layers_tw.clear()

        renderlayers = cmds.ls(type="renderLayer")

        if "defaultRenderLayer" in renderlayers:
            renderlayers.remove("defaultRenderLayer")
            renderlayers.append("masterLayer")

        for render_layer in renderlayers:
            render_layer_item = QtWidgets.QTreeWidgetItem()
            render_layer_item.setText(0, render_layer)

            if render_layer != "masterLayer":
                render_layer_item.setFlags(render_layer_item.flags() | QtCore.Qt.ItemIsEditable)
            self.render_layers_tw.addTopLevelItem(render_layer_item)

            current_render_layer = cmds.editRenderLayerGlobals(query=True, currentRenderLayer=True)

            if render_layer == current_render_layer or (
                    render_layer == "masterLayer" and current_render_layer == "defaultRenderLayer"):
                render_layer_item.setSelected(True)

    def update_current_set(self, current_item=None):
        self.current_set_item = current_item

        if current_item is not None:
            self.current_set = self.current_set_item.text(0)
        else:
            self.current_set = None

        self.update_set_members()

    def sets_tw_rename_callback(self, item, column):
        prev_set_name = self.current_set
        new_set_name = item.text(0)

        cmds.rename(self.current_set, new_set_name)

        self.update_current_set(item)

        self.log.result("Renamed {0} to {1}".format(prev_set_name, new_set_name))

    def update_sets(self):
        self.sets_tw.clear()
        self.update_current_set()

        sets = []
        for objectset in cmds.ls(type="objectSet"):
            if cmds.nodeType(objectset) != "objectSet":
                continue
            sets.append(objectset)

        for set in sets:
            if set.startswith("default") or set.startswith("initial"):
                continue

            item = QtWidgets.QTreeWidgetItem()
            item.setText(0, str(set))
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
            self.sets_tw.addTopLevelItem(item)

        self.update_set_members()

    def update_set_members(self):
        self.set_members_tw.clear()

        if self.current_set is None:
            return

        members = cmds.sets(self.current_set, q=True)

        if members is None:
            return

        for m in members:
            item = QtWidgets.QTreeWidgetItem()
            item.setText(0, str(m))
            self.set_members_tw.addTopLevelItem(item)

    def create_create_widgets(self):
        lights_items = ['VRayLightRect', 'VRayLightSphere', 'VRayLightDome', 'DistantLight']

        modifiers_items = ['Default', 'Hidden', 'Matte']

        volumes_items = ['Volume Render Layer', 'Volume Box']

        other_items = ['Displacement Nodes']

        categories = {
            "Lights": lights_items,
            "Modifiers": modifiers_items,
            "Volumes": volumes_items,
            "Other": other_items
        }

        for cat, items in categories.items():
            cat_item = QtWidgets.QTreeWidgetItem()
            cat_item.setText(0, cat)

            for item in items:
                new_item = QtWidgets.QTreeWidgetItem()
                new_item.setText(0, item)

                cat_item.addChild(new_item)

            self.create_tw.addTopLevelItem(cat_item)

            cat_item.setExpanded(True)

    def add_set(self):
        new_set = cmds.sets(empty=True)[0]

        self.log.result("Created " + new_set)

        self.update_sets()

    def remove_set(self):
        if self.current_set is None:
            return

        cmds.delete(self.current_set)

        self.log.result("Deleted " + self.current_set)

        self.update_sets()

    def add_to_set(self):
        print self.current_set

        for obj in cmds.ls(sl=True):
            cmds.sets(obj, edit=True, add=self.current_set)

        self.update_set_members()

    def remove_from_set(self):
        print self.current_set

        for obj in cmds.ls(sl=True):
            cmds.sets(obj, edit=True, rm=self.current_set)

        self.update_set_members()

    def duplicate_set(self):
        if self.current_set is None:
            return

        new_set = cmds.duplicate(self.current_set)[0]

        try:
            for obj in cmds.sets(self.current_set, q=True):
                cmds.sets(obj, edit=True, add=new_set)
        except TypeError:
            pass

        self.update_sets()

        for i in range(self.sets_tw.topLevelItemCount()):
            if self.sets_tw.topLevelItem(i).text(0) == new_set:
                self.update_current_set(self.sets_tw.topLevelItem(i))

                self.update_set_members()

                self.sets_tw.topLevelItem(i).setSelected(True)

        self.log.result("Created " + new_set)

    def console_tw_item_changed_callback(self):
        selected_light_item = self.console_tw.currentItem()
        light = selected_light_item.text(2)

        print light

        cmds.select(light)


def main():
    try:
        dialog.close()
        dialog.deleteLater()
    except:
        pass

    dialog = LightingConsole()
    dialog.show()


if __name__ == "__main__":
    main()
