from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import pymel.core as pm
import vray

from pyqt_commons import MWidgets

reload(MWidgets)

from maya_core.lighting_console.constants import *

from maya_core.common_tools import logger

log = logger.Logger()


class RenderLayersWidget(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)
    push_properties = QtCore.Signal(object)
    properties_refresh_attr = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super(RenderLayersWidget, self).__init__(*args, **kwargs)

        self.setObjectName("RenderLayersWidget")

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

        render_layers_header_layout = QtWidgets.QHBoxLayout()
        render_layers_header_layout.setSpacing(GLOBAL_SPACING)

        render_layers_header_layout.addWidget(self.render_layers_header_lbl)

        render_layers_btn_layout = QtWidgets.QHBoxLayout()
        render_layers_btn_layout.setSpacing(GLOBAL_SPACING)

        render_layers_btn_layout.addStretch()
        render_layers_btn_layout.addWidget(self.render_layer_refresh_btn)
        render_layers_btn_layout.addWidget(self.render_layer_add_btn)
        render_layers_btn_layout.addWidget(self.render_layer_remove_btn)
        render_layers_btn_layout.addWidget(self.render_layer_duplicate_btn)

        render_layers_header_layout.addLayout(render_layers_btn_layout)

        render_layers_layout.addLayout(render_layers_header_layout)

        render_layers_layout.addWidget(self.render_layers_tw)

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

        self.render_layers_tw.itemSelectionChanged.connect(self.update_current_rl)
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
        for obj in cmds.ls(sl=1):
            try:
                cmds.editRenderLayerMembers(self.current_rl, obj)
            except Exception as e:
                print e
                continue

    def remove_from_layer(self):
        for obj in cmds.ls(sl=1):
            try:
                cmds.editRenderLayerMembers(self.current_rl, obj, remove=True)
            except Exception as e:
                print e
                continue

    def refresh_layers(self):
        self.update_render_layers()

    def add_layer(self):
        rl = cmds.createRenderLayer(empty=True)
        self.log_event.emit("result", "Created " + rl)
        self.update_render_layers()

    def update_current_rl(self):
        if not self.render_layers_tw.selectedItems():
            self.current_rl_item = None
            self.current_rl = None
            return

        self.current_rl_item = self.render_layers_tw.selectedItems()[0]
        self.current_rl = self.current_rl_item.text(0)

        if self.current_rl == "masterLayer":
            cmds.editRenderLayerGlobals(crl="defaultRenderLayer")
            log.info("Switching layers")
        else:
            log.info("Switching layers")
            cmds.editRenderLayerGlobals(crl=self.current_rl)

        self.properties_refresh_attr.emit()

    def render_layers_tw_rename_callback(self, item, column):
        prev_rl_name = self.current_rl
        new_rl_name = item.text(0)

        cmds.rename(self.current_rl, new_rl_name)

        self.update_current_rl(item)

        self.log_event.emit("result", "Renamed {0} to {1}".format(prev_rl_name, new_rl_name))

    def update_render_layers(self):
        self.render_layers_tw.clear()
        self.render_layers_tw.blockSignals(True)

        renderlayers = sorted(cmds.ls(type='renderLayer'), reverse=True, key=lambda r: cmds.getAttr(r + ".displayOrder"))

        renderlayers.remove("defaultRenderLayer")
        renderlayers.append("defaultRenderLayer")

        rl_item_data = {}
        for render_layer in renderlayers:
            render_layer_item = QtWidgets.QTreeWidgetItem()
            render_layer_item.setText(0, render_layer)

            if render_layer != "masterLayer":
                render_layer_item.setFlags(render_layer_item.flags() | QtCore.Qt.ItemIsEditable)
            self.render_layers_tw.addTopLevelItem(render_layer_item)

            rl_item_data[render_layer] = render_layer_item

        if rl_item_data:
            current_rl = cmds.editRenderLayerGlobals(query=True, currentRenderLayer=True)

            rl_item_data[current_rl].setSelected(True)

        self.render_layers_tw.blockSignals(False)

