from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import pymel.core as pm
import vray

from pyqt_commons import MWidgets

reload(MWidgets)

from maya_core.lighting_console.constants import *


class ModifiersWidgetProperties(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)

    def __init__(self, *args, **kwargs):
        super(ModifiersWidgetProperties, self).__init__(*args, **kwargs)

        self.setObjectName("ModifiersWidgetProperties")

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.setContentsMargins(0, 0, 0, 0)

    def create_actions(self):
        pass

    def create_widgets(self):
        pass

    def create_layout(self):
        pass

    def create_connections(self):
        pass


class ModifierItemWidget(QtWidgets.QTreeWidgetItem):

    def __init__(self, node, preset=None, parent=None, *args, **kwargs):
        super(ModifierItemWidget, self).__init__(*args, **kwargs)

        self.setFlags(self.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable)

        self.pm_node = node
        self.properties_widget = ModifiersWidgetProperties()

        if self.pm_node.ignore.get():
            self.setCheckState(0, QtCore.Qt.Unchecked)
        else:
            self.setCheckState(0, QtCore.Qt.Checked)

        self.setText(0, "     " + str(self.pm_node))

        self.setSizeHint(0, QtCore.QSize(100, 30))

        if preset:
            self.preset = preset
        else:
            self.preset = "Custom"


class ModifiersWidget(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)

    def __init__(self, *args, **kwargs):
        super(ModifiersWidget, self).__init__(*args, **kwargs)

        self.setObjectName("ModifiersWidget")

        self.setContentsMargins(0, 0, 0, 0)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

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

        self.modifiers_refresh_btn = MWidgets.ImagePushButton(30, 30)
        self.modifiers_refresh_btn.set_image("F:\\share\\tools\\shelf_icons\\refresh.png")
        self.modifiers_refresh_btn.setFixedSize(30, 30)

        self.modifiers_tw = QtWidgets.QTreeWidget()
        modifiers_tw_header = QtWidgets.QTreeWidgetItem(['Modifier'])
        self.modifiers_tw.setHeaderItem(modifiers_tw_header)
        self.modifiers_tw.resizeColumnToContents(0)
        self.modifiers_tw.setAlternatingRowColors(True)

        self.refresh_modifiers()

        self.modifier_objects_tw = QtWidgets.QTreeWidget()
        linked_sets_tw_header = QtWidgets.QTreeWidgetItem(['Modifier Objects'])
        self.modifier_objects_tw.setHeaderItem(linked_sets_tw_header)
        self.modifier_objects_tw.setMaximumHeight(RES_Y * .15)

        self.modifiers_tw.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.modifiers_tw.customContextMenuRequested.connect(self.show_modifiers_tw_context_menu)

        self.modifier_objects_tw.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.modifier_objects_tw.customContextMenuRequested.connect(self.show_modifier_objects_tw_context_menu)

    def create_layout(self):
        modifiers_layout = QtWidgets.QVBoxLayout(self)
        modifiers_layout.setSpacing(GLOBAL_SPACING)

        modifiers_btn_layout = QtWidgets.QHBoxLayout()
        modifiers_btn_layout.setSpacing(GLOBAL_SPACING)

        modifiers_btn_layout.addWidget(self.modifiers_header_lbl)
        modifiers_btn_layout.addStretch()
        modifiers_btn_layout.addWidget(self.modifiers_refresh_btn)
        modifiers_btn_layout.addWidget(self.modifiers_add_btn)
        modifiers_btn_layout.addWidget(self.modifiers_remove_btn)
        modifiers_btn_layout.addWidget(self.modifiers_duplicate_btn)

        modifiers_layout.addLayout(modifiers_btn_layout)

        modifiers_layout.addWidget(self.modifiers_tw)
        modifiers_layout.addWidget(self.modifier_objects_tw)

    def create_connections(self):
        self.modifiers_tw.currentItemChanged.connect(self.update_current_modifier)
        self.modifiers_tw.itemChanged.connect(self.modifiers_tw_rename_callback)

        self.modifiers_refresh_btn.clicked.connect(self.refresh_modifiers)
        self.modifiers_add_btn.clicked.connect(self.create_modifier)

    def show_modifiers_tw_context_menu(self, eventPosition):
        child = self.childAt(self.sender().mapTo(self, eventPosition))
        self.current_modifier_item = self.modifiers_tw.itemAt(eventPosition)

        contextMenu = QtWidgets.QMenu(self)

        action = contextMenu.exec_(child.mapToGlobal(eventPosition))

    def show_modifier_objects_tw_context_menu(self, eventPosition):
        child = self.childAt(self.sender().mapTo(self, eventPosition))
        self.current_modifier_object_item = self.modifier_objects_tw.itemAt(eventPosition)

        contextMenu = QtWidgets.QMenu(self)

    def update_current_modifier(self, current_item=None):
        self.current_modifier_item = current_item

        if current_item:
            self.current_modifier = str(self.current_modifier_item.pm_node)
        else:
            self.current_modifier = None

        self.update_modifier_members()

    def update_modifier_members(self):
        self.modifier_objects_tw.clear()

        if self.current_modifier is None:
            return

        members = cmds.sets(self.current_modifier, q=True)

        if members is None:
            return

        for m in members:
            item = QtWidgets.QTreeWidgetItem()
            item.setText(0, str(m))
            self.modifier_objects_tw.addTopLevelItem(item)

    def modifiers_tw_rename_callback(self, item, column):
        try:
            item.pm_node.rename(item.text(0))
            item.setText(0, "     " + str(item.pm_node))
        except Exception:
            item.setText(0, "     " + str(item.pm_node))

    def refresh_modifiers(self):
        self.modifiers_tw.clear()

        nodes = pm.ls(type="VRayObjectProperties")

        for node in nodes:
            new_item = ModifierItemWidget(node)

            self.modifiers_tw.addTopLevelItem(new_item)

    def create_modifier(self):
        modifier_node = pm.PyNode(pm.createNode("VRayObjectProperties"))

        self.refresh_modifiers()

    def set_preset(self, preset):
        pass

    def add_to_modifier(self):
        current_modifier = str(self.current_modifier_item.pm_node)

        for obj in cmds.ls(sl=True):
            cmds.sets(obj, edit=True, add=current_modifier)

        if len(cmds.ls(sl=True)) > 1:
            self.log_event.emit("result", "Added objects to {0}".format(current_modifier))
        elif len(cmds.ls(sl=True)) == 1:
            self.log_event.emit("result", "Added {0} to {1}".format(cmds.ls(sl=True)[0]), current_modifier)

        self.update_set_members()

    def remove_from_modifier(self):
        current_modifier = str(self.current_modifier_item.pm_node)

        for obj in cmds.ls(sl=True):
            cmds.sets(obj, edit=True, rm=current_modifier)

        if len(cmds.ls(sl=True)) > 1:
            self.log_event.emit("result", "Removed objects from {0}".format(current_modifier))
        elif len(cmds.ls(sl=True)) == 1:
            self.log_event.emit("result", "Removed {0} from {1}".format(cmds.ls(sl=True)[0]), current_modifier)

    def show_modifier_objects_tw_context_menu(self, eventPosition):
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
