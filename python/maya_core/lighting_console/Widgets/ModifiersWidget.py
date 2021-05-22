from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import pymel.core as pm
import vray

from pyqt_commons import MWidgets

reload(MWidgets)

from maya_core.lighting_console import constants
from maya_core.lighting_console import modifiers_constants
from maya_core.lighting_console.Widgets import PropertiesWidget

reload(constants)
reload(modifiers_constants)


class ModifiersWidgetProperties(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)
    renamed = QtCore.Signal(str)

    def __init__(self, node, *args, **kwargs):
        super(ModifiersWidgetProperties, self).__init__(*args, **kwargs)
        self.setContentsMargins(0, 0, 0, 0)

        self.setMinimumSize(constants.RES_X * .95 * .125, constants.RES_Y * .875 * .575 * .9)

        self.pm_node = node
        self.widgets = []

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.header_lbl = QtWidgets.QLabel("VRayObjectProperties: ")
        self.header_le = QtWidgets.QLineEdit()
        self.header_le.setText(str(self.pm_node))

        for attr_group, attr_group_data in modifiers_constants.MODIFIERS['attr_groups'].items():
            group_label_widget = QtWidgets.QLabel(attr_group_data['label'])
            group_label_widget.setStyleSheet("font-weight: bold;")
            self.widgets.append(group_label_widget)
            self.widgets.append(MWidgets.QHLine())

            for attr in attr_group_data['attrs']:
                attr_widget = None
                if attr in modifiers_constants.MODIFIERS['attrs'].keys():
                    try:
                        attr_data = modifiers_constants.MODIFIERS['attrs'].get(attr)
                        attr_widget_class = attr_data['widget_class']

                        widget_class = getattr(PropertiesWidget, attr_widget_class)
                        attr_widget = widget_class(self.pm_node, attr_data)
                    except Exception as e:
                        print "error: " + str(e)

                if attr_widget:
                    self.widgets.append(attr_widget)

            self.widgets.append(MWidgets.VSpacerWidget(20))

    def create_layout(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setSpacing(8)

        header_layout = QtWidgets.QHBoxLayout()
        header_layout.addWidget(self.header_lbl)
        header_layout.addWidget(self.header_le)

        self.main_layout.addLayout(header_layout)
        self.main_layout.addWidget(MWidgets.QHLine())

        scroll_area_widget = QtWidgets.QScrollArea()
        scroll_area_widget.setWidgetResizable(True)
        scroll_area_widget.setFrameShape(QtWidgets.QFrame.NoFrame)

        properties_widget = QtWidgets.QWidget()
        properties_layout = QtWidgets.QVBoxLayout(properties_widget)
        properties_layout.setContentsMargins(0, 0, 0, 0)
        properties_layout.setSpacing(8)

        # Add all widgets
        for widget in self.widgets:
            properties_layout.addWidget(widget)

        properties_layout.addStretch()

        scroll_area_widget.setWidget(properties_widget)

        self.main_layout.addWidget(scroll_area_widget)

    def create_connections(self):
        self.header_le.returnPressed.connect(self.rename)

    def rename(self):
        try:
            pm.rename(self.pm_node, self.header_le.text())
        except Exception:
            pass

        self.header_le.setText(str(self.pm_node))
        self.renamed.emit(str(self.pm_node))

    def refresh_attr(self):
        for widget in self.widgets:
            if hasattr(widget, 'refresh_attr'):
                widget.refresh_attr()


class ModifierObjectWidgetItem(QtWidgets.QTreeWidgetItem):

    def __init__(self, node, *args, **kwargs):
        super(ModifierObjectWidgetItem, self).__init__(*args, **kwargs)

        self.setText(0, node)
        self.pm_node = pm.PyNode(node)

        self.properties_widget = ModifiersWidgetProperties(self.pm_node)


class ModifierWidgetItem(QtWidgets.QTreeWidgetItem):

    def __init__(self, node, preset=None, parent=None, *args, **kwargs):
        super(ModifierWidgetItem, self).__init__(*args, **kwargs)

        self.setFlags(self.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable)

        self.pm_node = node
        self.properties_widget = ModifiersWidgetProperties(self.pm_node)

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
    push_properties = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        super(ModifiersWidget, self).__init__(*args, **kwargs)

        self.setObjectName("ModifiersWidget")

        self.setContentsMargins(0, 0, 0, 0)

        self.current_modifier_item = None
        self.current_modifier_object_item = None

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        self.create_default_modifier_action = QtWidgets.QAction("Create Default")
        self.create_hidden_modifier_action = QtWidgets.QAction("Create Hidden")
        self.create_matte_modifier_action = QtWidgets.QAction("Create Matte")

        self.set_to_default_action = QtWidgets.QAction("Set to Default")
        self.set_to_hidden_action = QtWidgets.QAction("Set to Hidden")
        self.set_to_matte_action = QtWidgets.QAction("Set to Matte")

        self.delete_modifier_action = QtWidgets.QAction("Delete Modifier")
        self.duplicate_modifier_action = QtWidgets.QAction("Duplicate Modifier")

        self.add_to_modifier_action = QtWidgets.QAction("Add selected to modifier")
        self.remove_from_modifier_action = QtWidgets.QAction("Remove selected from modifier")

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

        self.modifiers_tw = MWidgets.MTreeWidget()
        modifiers_tw_header = QtWidgets.QTreeWidgetItem(['Modifier'])
        self.modifiers_tw.setHeaderItem(modifiers_tw_header)
        self.modifiers_tw.resizeColumnToContents(0)
        self.modifiers_tw.setAlternatingRowColors(True)

        self.refresh_modifiers()

        self.modifier_objects_tw = QtWidgets.QTreeWidget()
        linked_sets_tw_header = QtWidgets.QTreeWidgetItem(['Modifier Objects'])
        self.modifier_objects_tw.setHeaderItem(linked_sets_tw_header)
        self.modifier_objects_tw.setMaximumHeight(constants.RES_Y * .15)

        self.modifiers_tw.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.modifiers_tw.customContextMenuRequested.connect(self.show_modifiers_tw_context_menu)

        self.modifier_objects_tw.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.modifier_objects_tw.customContextMenuRequested.connect(self.show_modifier_objects_tw_context_menu)

    def create_layout(self):
        modifiers_layout = QtWidgets.QVBoxLayout(self)
        modifiers_layout.setSpacing(constants.GLOBAL_SPACING)

        modifiers_btn_layout = QtWidgets.QHBoxLayout()
        modifiers_btn_layout.setSpacing(constants.GLOBAL_SPACING)

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
        self.modifiers_tw.itemSelectionChanged.connect(self.update_current_modifier)
        self.modifiers_tw.itemChanged.connect(self.modifiers_tw_rename_callback)

        self.modifiers_refresh_btn.clicked.connect(self.refresh_modifiers)
        self.modifiers_add_btn.clicked.connect(self.create_modifier)

        self.create_default_modifier_action.triggered.connect(self.create_modifier)

        self.duplicate_modifier_action.triggered.connect(self.duplicate_modifier)
        self.delete_modifier_action.triggered.connect(self.delete_modifier)

        self.add_to_modifier_action.triggered.connect(self.add_to_modifier)
        self.remove_from_modifier_action.triggered.connect(self.remove_from_modifier)

    def duplicate_modifier(self):
        try:
            pm.duplicate(self.current_modifier_item.pm_node, un=True)
            self.refresh_modifiers()
        except Exception:
            pass

    def delete_modifier(self):
        try:
            pm.delete(self.current_modifier_item.pm_node)
            self.refresh_modifiers()
        except Exception:
            pass

    def show_modifiers_tw_context_menu(self, eventPosition):
        child = self.childAt(self.sender().mapTo(self, eventPosition))
        self.current_modifier_item = self.modifiers_tw.itemAt(eventPosition)

        contextMenu = QtWidgets.QMenu(self)

        if self.current_modifier_item is not None:
            about_action = QtWidgets.QAction(self.current_modifier_item.text(0).strip())
            about_action.triggered.connect(lambda: pm.select(self.current_modifier_item.pm_node, noExpand=True))
            contextMenu.addAction(about_action)
            contextMenu.addSeparator()

            contextMenu.addAction(self.duplicate_modifier_action)
            contextMenu.addAction(self.delete_modifier_action)

            if len(pm.ls(sl=1)) > 0:
                contextMenu.addSeparator()
                contextMenu.addAction(self.add_to_modifier_action)
                contextMenu.addAction(self.remove_from_modifier_action)

            contextMenu.addSeparator()
            contextMenu.addAction(self.set_to_default_action)
            contextMenu.addAction(self.set_to_hidden_action)
            contextMenu.addAction(self.set_to_matte_action)

        else:
            contextMenu.addAction(self.create_default_modifier_action)
            contextMenu.addAction(self.create_hidden_modifier_action)
            contextMenu.addAction(self.create_matte_modifier_action)

        action = contextMenu.exec_(child.mapToGlobal(eventPosition))

    def show_modifier_objects_tw_context_menu(self, eventPosition):
        child = self.childAt(self.sender().mapTo(self, eventPosition))
        self.current_modifier_object_item = self.modifier_objects_tw.itemAt(eventPosition)

        contextMenu = QtWidgets.QMenu(self)

        if self.current_modifier_item is not None:
            if self.current_modifier_object_item is None:
                contextMenu.addAction(self.add_to_modifier_action)
            else:
                about_action = QtWidgets.QAction(self.current_modifier_object_item.text(0))
                contextMenu.addAction(about_action)
                contextMenu.addSeparator()

            if self.current_modifier_object_item is None and self.selected_in_modifier():
                contextMenu.addAction(self.remove_from_modifier_action)
            elif self.current_modifier_object_item is not None:
                remove_action = QtWidgets.QAction(
                    "Remove {} from modifier".format(str(self.current_modifier_object_item.pm_node)))
                remove_action.triggered.connect(self.remove_from_modifier)
                contextMenu.addAction(remove_action)

        action = contextMenu.exec_(child.mapToGlobal(eventPosition))

    def selected_in_modifier(self, objs=None):
        if objs is None:
            objs = pm.ls(sl=1)

        selected_in_modifier = []

        for obj in objs:
            if cmds.sets(str(obj), im=str(self.current_modifier_item.pm_node)):
                selected_in_modifier.append(obj)

        return selected_in_modifier

    def update_current_modifier(self):
        if not self.modifiers_tw.selectedItems():
            self.push_properties.emit(None)
            return

        self.current_modifier_item = self.modifiers_tw.selectedItems()[0]

        if self.current_modifier_item:
            self.current_modifier = str(self.current_modifier_item.pm_node)
        else:
            self.current_modifier = None

        self.update_modifier_members()
        self.show_properties(self.current_modifier_item)

    def update_modifier_members(self):
        self.modifier_objects_tw.clear()

        if self.current_modifier is None:
            return

        members = cmds.sets(self.current_modifier, q=True)

        if members is None:
            return

        for m in members:
            item = ModifierObjectWidgetItem(m)
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
            new_item = ModifierWidgetItem(node)

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

        self.update_modifier_members()

    def remove_from_modifier(self):
        current_modifier = str(self.current_modifier_item.pm_node)

        if self.current_modifier_object_item is not None:
            cmds.sets(str(self.current_modifier_object_item.pm_node), edit=True, rm=current_modifier)
        else:
            for obj in cmds.ls(sl=True):
                cmds.sets(obj, edit=True, rm=current_modifier)

        self.update_modifier_members()

    def show_properties(self, item):
        self.push_properties.emit(item.properties_widget)
