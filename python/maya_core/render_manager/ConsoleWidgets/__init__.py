from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import vray

from pyqt_commons import MWidgets
from maya_core.material_builder import material_builder_ui

SCALE = 1
RES_X = 2550 * SCALE
RES_Y = 1320 * SCALE
GLOBAL_SPACING = 7


class RenderLayersWidget(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)

    def __init__(self, *args, **kwargs):
        super(RenderLayersWidget, self).__init__(*args, **kwargs)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.setContentsMargins(0, 0, 0, 0)

    def create_actions(self):
        # Render Layers Actions
        self.add_layer_action = QtWidgets.QAction("Add Layer")
        self.delete_layer_action = QtWidgets.QAction("Delete Layer")
        self.duplicate_layer_action = QtWidgets.QAction("Duplicate Layer")
        self.add_to_layer_action = QtWidgets.QAction("Add selected to layer")
        self.remove_from_layer_action = QtWidgets.QAction("Remove from layer")
        self.refresh_action = QtWidgets.QAction("Refresh Layers")

    def create_widgets(self):
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

    def create_layout(self):
        render_layers_layout = QtWidgets.QVBoxLayout(self)
        render_layers_layout.setSpacing(GLOBAL_SPACING)

        render_layers_layout.addWidget(self.render_layers_header_lbl)
        render_layers_layout.addWidget(self.render_layers_tw)

        render_layers_btn_layout = QtWidgets.QHBoxLayout()
        render_layers_btn_layout.setSpacing(GLOBAL_SPACING)

        render_layers_btn_layout.addStretch()
        render_layers_btn_layout.addWidget(self.render_layer_refresh_btn)
        render_layers_btn_layout.addWidget(self.render_layer_add_btn)
        render_layers_btn_layout.addWidget(self.render_layer_remove_btn)
        render_layers_btn_layout.addWidget(self.render_layer_duplicate_btn)

        render_layers_layout.addLayout(render_layers_btn_layout)

    def create_connections(self):
        # Render Layers
        self.add_layer_action.triggered.connect(self.add_layer)
        self.delete_layer_action.triggered.connect(self.delete_layer)
        self.duplicate_layer_action.triggered.connect(self.duplicate_layer)
        self.add_to_layer_action.triggered.connect(self.add_to_layer)
        self.remove_from_layer_action.triggered.connect(self.remove_from_layer)
        self.refresh_action.triggered.connect(self.refresh_layers)

        self.render_layer_add_btn.clicked.connect(self.add_layer)
        self.render_layer_remove_btn.clicked.connect(self.delete_layer)
        self.render_layer_refresh_btn.clicked.connect(self.refresh_layers)
        self.render_layer_duplicate_btn.clicked.connect(self.duplicate_layer)

        self.render_layers_tw.currentItemChanged.connect(self.update_current_rl)
        self.render_layers_tw.itemChanged.connect(self.render_layers_tw_rename_callback)

    def show_rl_context_menu(self, eventPosition):
        child = self.childAt(self.sender().mapTo(self, eventPosition))
        self.current_rl_item = self.render_layers_tw.itemAt(eventPosition)

        contextMenu = QtWidgets.QMenu(self)

        if self.current_rl_item is None:
            contextMenu.addAction(self.add_layer_action)
        else:
            about_action = QtWidgets.QAction(self.current_rl_item.text(0))

            contextMenu.addAction(about_action)
            contextMenu.addSeparator()
            contextMenu.addAction(self.delete_layer_action)
            contextMenu.addAction(self.duplicate_layer_action)
            contextMenu.addSeparator()
            contextMenu.addAction(self.add_to_layer_action)
            contextMenu.addAction(self.remove_from_layer_action)

        contextMenu.addSeparator()
        contextMenu.addAction(self.refresh_action)

        action = contextMenu.exec_(child.mapToGlobal(eventPosition))

    def delete_layer(self):
        current_layer = self.current_rl_item.text(0)

        if current_layer == "masterLayer":
            self.log_event.emit("error", "Cannot delete default render layer")
            return

        if cmds.objExists(current_layer):
            if cmds.editRenderLayerGlobals(q=True, crl=True) == current_layer:
                cmds.editRenderLayerGlobals(crl="defaultRenderLayer")

            cmds.delete(current_layer)

            self.log_event.emit("result", "Deleted " + current_layer)

        self.update_render_layers()

    def duplicate_layer(self):
        if self.current_rl is None:
            return

        current_rl = self.current_rl

        if self.current_rl == "masterLayer":
            current_rl = "defaultRenderLayer"

        new_rl = cmds.duplicate(current_rl)[0]

        self.log_event.emit("result", "Created " + new_rl)

        self.update_render_layers()

    def add_to_layer(self):
        self.log_event.emit("info", "TODO: add_to_layer")

    def remove_from_layer(self):
        self.log_event.emit("info", "TODO: remove_from_layer")

    def refresh_layers(self):
        self.update_render_layers()

    def add_layer(self):
        rl = cmds.createRenderLayer(empty=True)
        self.log_event.emit("result", "Created " + rl)
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

        self.log_event.emit("result", "Renamed {0} to {1}".format(prev_rl_name, new_rl_name))

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


class ModifiersWidget(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)

    def __init__(self, *args, **kwargs):
        super(ModifiersWidget, self).__init__(*args, **kwargs)

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


class AOVsWidget(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)

    def __init__(self, *args, **kwargs):
        super(AOVsWidget, self).__init__(*args, **kwargs)

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


class SetsWidget(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)

    def __init__(self, *args, **kwargs):
        super(SetsWidget, self).__init__(*args, **kwargs)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.setContentsMargins(0, 0, 0, 0)

    def create_actions(self):
        self.add_set_action = QtWidgets.QAction("Add Set")
        self.remove_set_action = QtWidgets.QAction("Remove Set")
        self.duplicate_set_action = QtWidgets.QAction("Duplicate Set")
        self.add_to_set_action = QtWidgets.QAction("Add selected to set")
        self.remove_from_set_action = QtWidgets.QAction("Remove from set")
        self.refresh_sets_action = QtWidgets.QAction("Refresh Sets")

    def create_widgets(self):
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

    def create_layout(self):
        sets_layout = QtWidgets.QVBoxLayout(self)
        sets_layout.setSpacing(GLOBAL_SPACING)

        sets_btn_layout = QtWidgets.QHBoxLayout()
        sets_btn_layout.setSpacing(GLOBAL_SPACING)

        sets_btn_layout.addWidget(self.sets_header_lbl)
        sets_btn_layout.addStretch()
        sets_btn_layout.addWidget(self.sets_refresh_btn)
        sets_btn_layout.addWidget(self.add_set_btn)
        sets_btn_layout.addWidget(self.remove_set_btn)
        sets_btn_layout.addWidget(self.sets_duplicate_btn)

        sets_layout.addLayout(sets_btn_layout)

        sets_tw_layout = QtWidgets.QHBoxLayout()
        sets_tw_layout.setSpacing(GLOBAL_SPACING)
        sets_tw_layout.addWidget(self.sets_tw)
        sets_tw_layout.addWidget(self.set_members_tw)

        sets_layout.addLayout(sets_tw_layout)

    def create_connections(self):
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

        # self.log.result("Renamed {0} to {1}".format(prev_set_name, new_set_name))

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

    def add_set(self):
        new_set = cmds.sets(empty=True)[0]

        # self.log.result("Created " + new_set)

        self.update_sets()

    def remove_set(self):
        if self.current_set is None:
            return

        cmds.delete(self.current_set)

        # self.log.result("Deleted " + self.current_set)

        self.update_sets()

    def add_to_set(self):
        for obj in cmds.ls(sl=True):
            cmds.sets(obj, edit=True, add=self.current_set)

        self.update_set_members()

    def remove_from_set(self):
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

        # self.log.result("Created " + new_set)


class RenderOverridesWidget(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)

    def __init__(self, *args, **kwargs):
        super(RenderOverridesWidget, self).__init__(*args, **kwargs)

        self.setContentsMargins(0, 0, 0, 0)
        self.vray_settings = pm.PyNode("vraySettings")

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


class ToolButtons(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)
    light_created = QtCore.Signal(str)

    def __init__(self, *args, **kwargs):
        super(ToolButtons, self).__init__(*args, **kwargs)

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


class PropertiesWidget(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)

    def __init__(self, *args, **kwargs):
        super(PropertiesWidget, self).__init__(*args, **kwargs)

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
