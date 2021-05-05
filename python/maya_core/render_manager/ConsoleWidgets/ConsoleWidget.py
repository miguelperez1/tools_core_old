from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import pymel.core as pm
import vray

import os
import math

from pyqt_commons import MWidgets
from maya_core.material_builder import material_builder_ui

reload(MWidgets)

SCALE = 1
RES_X = 2550 * SCALE
RES_Y = 1320 * SCALE

ICONS = {
    "VRayLightRectShape": "C:\\Program Files\\Autodesk\\Maya2020\\vray\\icons\\shelf_LightRect_200.png",
    "VRayLightSphereShape": "C:\\Program Files\\Autodesk\\Maya2020\\vray\\icons\\shelf_LightSphere_200.png",
    "VRayLightDomeShape": "C:\\Program Files\\Autodesk\\Maya2020\\vray\\icons\\shelf_LightDome_200.png",
    "directionalLight": ":/directionallight.png",
    "connection_in": ":/hsUpStreamCon.png",
    "group": "F:\\share\\tools\\shelf_icons\\group.png"
}


class RecursiveNodeSearch(object):
    def _traverse(self, node, children):

        connections = []

        for c in pm.listRelatives(node, c=True):
            connections.append(str(c))

        for child in connections:
            children[child] = {}

    def get_nodes(self, node, children):
        self._traverse(node, children)

        for child in children:
            self._traverse(child, children[child])

    def search_nodes(self, node):
        children = {}
        self.get_nodes(node, children)

        return children


def convert_K_to_RGB(colour_temperature):
    """
    Converts from K to RGB, algorithm courtesy of
    http://www.tannerhelland.com/4430/convert-temperature-rgb-algorithm-code/
    """
    # range check
    if colour_temperature < 1000:
        colour_temperature = 1000
    elif colour_temperature > 40000:
        colour_temperature = 40000

    tmp_internal = colour_temperature / 100.0

    # red
    if tmp_internal <= 66:
        red = 255
    else:
        tmp_red = 329.698727446 * math.pow(tmp_internal - 60, -0.1332047592)
        if tmp_red < 0:
            red = 0
        elif tmp_red > 255:
            red = 255
        else:
            red = tmp_red

    # green
    if tmp_internal <= 66:
        tmp_green = 99.4708025861 * math.log(tmp_internal) - 161.1195681661
        if tmp_green < 0:
            green = 0
        elif tmp_green > 255:
            green = 255
        else:
            green = tmp_green
    else:
        tmp_green = 288.1221695283 * math.pow(tmp_internal - 60, -0.0755148492)
        if tmp_green < 0:
            green = 0
        elif tmp_green > 255:
            green = 255
        else:
            green = tmp_green

    # blue
    if tmp_internal >= 66:
        blue = 255
    elif tmp_internal <= 19:
        blue = 0
    else:
        tmp_blue = 138.5177312231 * math.log(tmp_internal - 10) - 305.0447927307
        if tmp_blue < 0:
            blue = 0
        elif tmp_blue > 255:
            blue = 255
        else:
            blue = tmp_blue

    return red / 255, green / 255, blue / 255


class LightConsoleTreeLightItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, light=None, parent=None, *args, **kwargs):
        super(LightConsoleTreeLightItem, self).__init__(*args, **kwargs)

        self.light = pm.PyNode(light)
        self.light_shape = self.light.getShape()
        self.light_type = pm.nodeType(self.light_shape)
        self.item_type = self.light_type
        self.pm_node = self.light

        if parent is not None:
            if cmds.objExists(str(parent)):
                self.parent_node = pm.PyNode(parent)
                try:
                    self.light.setParent(self.parent_node)
                except RuntimeError:
                    pass

        self.size = 35

        self.setSizeHint(2, QtCore.QSize(self.size, self.size))

        self.setFlags(self.flags() | QtCore.Qt.ItemIsEditable)

        self.setData(0, QtCore.Qt.UserRole, False)

        self.create_widgets()

        for col in range(10):
            if col == 3:
                continue
            self.setTextAlignment(col, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

    def create_widgets(self):
        self.widget_data = {}

        # Create sidgets
        enabled_cw = QtWidgets.QWidget()
        enabled_cb = QtWidgets.QCheckBox()

        enabled_layout = QtWidgets.QHBoxLayout(enabled_cw)
        enabled_layout.addStretch()
        enabled_layout.addWidget(enabled_cb)
        enabled_layout.addStretch()

        enabled_cb.stateChanged.connect(self.set_enabled)
        self.widget_data[1] = enabled_cw

        light_icon = MWidgets.PreviewLabel()
        light_icon.set_image(ICONS[self.light_type], self.size)
        self.widget_data[2] = light_icon

        color_cw = QtWidgets.QWidget()
        color_widget = MWidgets.ColorPickerTreeWidgetItemWidget(120, self.size * .8, self.light, self)
        color_layout = QtWidgets.QHBoxLayout(color_cw)
        color_layout.addStretch()
        color_layout.addWidget(color_widget)
        color_layout.addStretch()
        self.widget_data[5] = color_cw

        invisible_cw = QtWidgets.QWidget()
        invisible_cb = QtWidgets.QCheckBox()
        invisible_cb.stateChanged.connect(self.set_invisible)
        invisible_layout = QtWidgets.QHBoxLayout(invisible_cw)
        invisible_layout.addStretch()
        invisible_layout.addWidget(invisible_cb)
        invisible_layout.addStretch()

        tex_img_btn_cw = QtWidgets.QWidget()
        tex_img_btn = MWidgets.ImagePushButton(self.size * 1.25, self.size * 1.25)
        tex_img_btn.set_image(ICONS['connection_in'], self.size * 1.5)
        tex_img_btn_layout = QtWidgets.QHBoxLayout(tex_img_btn_cw)
        tex_img_btn_layout.addStretch()
        tex_img_btn_layout.addWidget(tex_img_btn)
        tex_img_btn_layout.addStretch()

        for connection in pm.listConnections(self.light_shape, c=1):
            if connection[0].endswith("Tex"):
                self.widget_data[7] = tex_img_btn_cw

        if self.light_type != "directionalLight":
            self.widget_data[10] = invisible_cw

        # Initialize widget values

        if self.light_type != "directionalLight":
            enabled_cb.setChecked(self.light.enabled.get())
        else:
            enabled_cb.setChecked(self.light.visibility.get())

        self.setText(3, str(self.light))

        exposure = math.log(self.light.intensity.get())
        self.setText(4, "{:.2f}".format(exposure))

        color = self.light.color.get()
        color_widget.set_button_color(color)

        if self.light_type != "directionalLight":
            temp = self.light.temperature.get()
            self.setText(6, str(int(temp)))
        else:
            self.setText(6, "6500")

        if self.light_type == "VRayLightRectShape":
            directional = self.light.directional.get()
            self.setText(8, "{:.3f}".format(directional))

        if self.light_type == "directionalLight":
            angle = self.light.lightAngle.get()
            self.setText(9, "{:.3f}".format(angle))

        if self.light_type != "directionalLight":
            invisible = self.light.invisible.get()
            invisible_cb.setChecked(invisible)

        self.setSizeHint(0, QtCore.QSize(35, 35))

    def set_enabled(self):
        enabled = self.widget_data[1].layout().itemAt(1).widget().isChecked()
        if self.light_type != "directionalLight":
            self.light.enabled.set(enabled)
        else:
            self.light.visibility.set(enabled)

    def set_invisible(self):
        if self.light_type != "directionalLight":
            invisible = self.widget_data[10].layout().itemAt(1).widget().isChecked()
            self.light.invisible.set(invisible)


class LightConsoleTreeGroupItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, name, parent=None, *args, **kwargs):
        super(LightConsoleTreeGroupItem, self).__init__(*args, **kwargs)

        self.name = name
        self.group = pm.PyNode(self.name)
        self.setText(3, str(self.group))
        self.item_type = "group"
        self.pm_node = self.group

        if parent is not None:
            if cmds.objExists(parent):
                self.parent_node = pm.PyNode(parent)
                try:
                    self.group.setParent(self.parent_node)
                except RuntimeError:
                    pass

        self.size = 40

        self.bold_font = QtGui.QFont()
        self.bold_font.setBold(True)
        self.setFont(3, self.bold_font)

        self.setSizeHint(2, QtCore.QSize(self.size, 60))

        self.setFlags(self.flags() | QtCore.Qt.ItemIsEditable)

        self.setData(0, QtCore.Qt.UserRole, True)
        self.setChildIndicatorPolicy(QtWidgets.QTreeWidgetItem.ShowIndicator)

        self.create_widgets()

    def create_widgets(self):
        self.widget_data = {}

        # Create widgets
        enabled_cw = QtWidgets.QWidget()
        enabled_cb = QtWidgets.QCheckBox()

        enabled_layout = QtWidgets.QHBoxLayout(enabled_cw)
        enabled_layout.addStretch()
        enabled_layout.addWidget(enabled_cb)
        enabled_layout.addStretch()

        enabled_cb.stateChanged.connect(self.set_enabled)
        self.widget_data[1] = enabled_cw

        light_icon = MWidgets.PreviewLabel()
        light_icon.set_image(ICONS["group"], self.size)
        self.widget_data[2] = light_icon

        enabled_cb.setChecked(self.group.visibility.get())

    def set_enabled(self):
        enabled = self.widget_data[1].layout().itemAt(1).widget().isChecked()

        self.group.visibility.set(enabled)


class LightConsoleTreeWidget(QtWidgets.QTreeWidget):
    log_event = QtCore.Signal(str, str)

    def dropEvent(self, event):
        self.dragged_item = event.source().selectedItems()[0]
        self.dragged_parent = self.dragged_item.parent()

        parent_node = None
        child_node = self.dragged_item.pm_node

        dropped_index = QtCore.QModelIndex(self.indexAt(event.pos()))

        if self.dragged_item:
            self.dropped_at_item = self.itemAt(event.pos())

            if self.dropped_at_item:
                self.dropped_parent = self.dropped_at_item.parent()
                dropped_at_is_group = self.dropped_at_item.data(0, QtCore.Qt.UserRole)

            else:
                self.dropped_parent = None
                dropped_at_is_group = False

            if dropped_index.isValid():
                if self.dragged_parent is None:
                    # remove from invisible
                    self.invisibleRootItem().removeChild(self.dragged_item)
                else:
                    # remove from parent
                    self.dragged_parent.removeChild(self.dragged_item)

                if dropped_at_is_group:
                    parent_node = self.dropped_at_item.pm_node
                    # parent item under group item
                    self.dropped_at_item.addChild(self.dragged_item)
                else:
                    if cmds.objExists("l_rig"):
                        parent_node = pm.PyNode("l_rig")

                    self.invisibleRootItem().insertChild(dropped_index.row(), self.dragged_item)
            else:
                if self.dragged_parent is None:
                    # remove from invisible
                    self.invisibleRootItem().removeChild(self.dragged_item)
                else:
                    # remove from parent
                    self.dragged_parent.removeChild(self.dragged_item)

                if cmds.objExists("l_rig"):
                    parent_node = pm.PyNode("l_rig")

                self.invisibleRootItem().addChild(self.dragged_item)

            if parent_node:
                child_node.setParent(parent_node)

            self.dragged_item.create_widgets()
            self.dragged_item.setSizeHint(2, QtCore.QSize(60, 60))

            for column, widget in self.dragged_item.widget_data.items():
                self.setItemWidget(self.dragged_item, column, widget)

    def __init__(self, *args, **kwargs):
        super(LightConsoleTreeWidget, self).__init__(*args, **kwargs)

        self.create_actions()

        self.header_item = QtWidgets.QTreeWidgetItem(
            ["", "Enabled", "", "Name", "Exposure", "Color", 'Temperature', "Tex", "Directional", 'Angle', 'Invisible',
             ''])
        self.setHeaderItem(self.header_item)

        self.setAlternatingRowColors(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.setColumnWidth(3, 250)
        self.setColumnWidth(4, 100)
        self.setColumnWidth(5, 150)

        self.itemDoubleClicked.connect(self.onTreeWidgetItemDoubleClicked)
        self.itemSelectionChanged.connect(self.select_light)
        self.itemChanged.connect(self.update_attribute)

        self.prev_attr_value = None

        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)

        self.create_connections()

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)
        self.resizeColumnToContents(2)
        self.resizeColumnToContents(10)

        self.get_light_rig()

    def create_actions(self):
        self.create_group_action = QtWidgets.QAction("Create Group")

        self.duplicate_item_action = QtWidgets.QAction("Duplicate")
        self.delete_item_action = QtWidgets.QAction("Delete")
        self.select_light_action = QtWidgets.QAction("Select Light")

        self.add_tex_action = QtWidgets.QAction("Use Tex")
        self.add_tex_action.setCheckable(True)

        self.delete_tex_action = QtWidgets.QAction("Delete Tex")

    def onTreeWidgetItemDoubleClicked(self, item, column):
        if self.can_edit_column(item, column):
            self.prev_attr_value = item.text(column)
            pass
            self.editItem(item, column)

    def update_attribute(self, item, column, value=None):
        if item.text(3) == "":
            return
        if self.prev_attr_value is None:
            return

        attribute = self.header_item.text(column).lower()
        if value is None:
            value = item.text(column)
        else:
            value = value

        if attribute != "name":
            attr = attribute
            value = float(value)
            if attribute == "exposure":
                attr = "intensity"
                item.setText(column, "{:.2f}".format(value))
                value = math.pow(2, value)

            elif attribute == "angle":
                attr = "lightAngle"
                item.setText(column, "{:.3f}".format(value))

            elif attribute == "temperature":
                color_btn_widget = self.itemWidget(item, 5).layout().itemAt(1).widget()
                color = convert_K_to_RGB(int(value))
                color_btn_widget.set_button_color(color, 1)
            else:
                item.setText(column, "{:.3f}".format(value))

            getattr(item.light, attr).set(float(value))

        # Needs to go here
        if attribute == "name":
            try:
                item.pm_node.rename(value.replace(" ", ""))
                item.setText(column, str(item.pm_node))
            except Exception as e:
                self.log_event.emit("error", e)
                item.setText(column, str(item.pm_node))
                return

    def can_edit_column(self, item, column):
        item_type = item.item_type

        column_editability = {
            "VRayLightRectShape": [3, 4, 5, 6, 8],
            "VRayLightSphereShape": [3, 4, 5, 6],
            "VRayLightDomeShape": [3, 4, 5, 6],
            "directionalLight": [3, 3, 4, 6, 9],
            "group": [3]
        }

        if column in column_editability[item_type]:
            return True
        return False

    def select_light(self):
        if len(self.selectedItems()) == 1:
            return

        selection = []
        for i in self.selectedItems():
            selection.append(i.text(3))
        cmds.select(selection)

    def create_light(self, light, parent):
        new_item = LightConsoleTreeLightItem(light, parent)

        self.addTopLevelItem(new_item)

        for column, widget in new_item.widget_data.items():
            self.setItemWidget(new_item, column, widget)

        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)
        self.resizeColumnToContents(2)
        self.resizeColumnToContents(10)

        return new_item

    def show_context_menu(self, event_position):
        context_menu = QtWidgets.QMenu(self)

        self.current_item = self.itemAt(event_position)

        if self.current_item is None:
            context_menu.addAction(self.create_group_action)
        else:
            pm_node = self.current_item.pm_node

            about_action = QtWidgets.QAction(str(pm_node))
            about_action.triggered.connect(lambda: pm.select(str(pm_node.getShape())))

            context_menu.addAction(about_action)
            context_menu.addSeparator()
            context_menu.addAction(self.duplicate_item_action)
            context_menu.addAction(self.delete_item_action)
            context_menu.addSeparator()

            if self.current_item.item_type in ["VRayLightRectShape", "VRayLightDomeShape"]:
                context_menu.addAction(self.add_tex_action)

                if self.current_item.item_type == "VRayLightRectShape":
                    self.add_tex_action.setChecked(pm_node.useRectTex.get())
                elif self.current_item.item_type == "VRayLightDomeShape":
                    self.add_tex_action.setChecked(pm_node.useDomeTex.get())

                has_tex = False

                for connection in pm.listConnections(self.current_item.pm_node.getShape(), c=1):
                    if connection[0].endswith("Tex"):
                        has_tex = True

                if has_tex:
                    context_menu.addAction(self.delete_tex_action)

        context_menu.exec_(self.mapToGlobal(event_position))

    def create_connections(self):
        self.create_group_action.triggered.connect(self.create_group)
        self.add_tex_action.toggled.connect(self.set_tex)
        self.delete_tex_action.triggered.connect(self.delete_tex)
        self.duplicate_item_action.triggered.connect(self.duplicate_item)
        self.delete_item_action.triggered.connect(self.delete_item)

    def duplicate_item(self):
        self.current_item.pm_node.duplicate(un=True)
        self.get_light_rig()

    def delete_item(self):
        pm.delete(self.current_item.pm_node)
        self.get_light_rig()

    def set_tex(self, use):
        light_type = self.current_item.item_type
        pm_node = self.current_item.pm_node
        pm_node.multiplyByTheLightColor.set(1)

        if light_type == "VRayLightRectShape":
            self.current_item.pm_node.useRectTex.set(use)

        elif light_type == "VRayLightDomeShape":
            self.current_item.pm_node.useDomeTex.set(use)

            # if not tex, create, if tex, pass

            # if not tex, create, if tex, pass
        has_tex = False

        for connection in pm.listConnections(self.current_item.pm_node.getShape(), c=1):
            if connection[0].endswith("Tex"):
                has_tex = True

        if not has_tex and use:
            self.log_event.emit("info", "need to create tex")

    def delete_tex(self):
        pm_node = self.current_item.pm_node

        for connection in pm.listConnections(pm_node.getShape(), c=1):
            if connection[0].endswith("Tex"):
                self.log_event.emit("info", "need to break tex")

    def create_group(self, name=None, parent="l_rig", startup=False):

        if startup:
            group = pm.PyNode(name)
        else:
            group = pm.PyNode(pm.group(em=True, n="l_group_temp"))

        new_group_item = LightConsoleTreeGroupItem(str(group), parent)

        self.addTopLevelItem(new_group_item)

        for column, widget in new_group_item.widget_data.items():
            self.setItemWidget(new_group_item, column, widget)

        return new_group_item

    def get_light_rig(self):
        self.clear()

        light_types = [
            'VRayLightRectShape',
            'VRayLightSphereShape',
            'VRayLightDomeShape',
            'directionalLight',
        ]

        all_nodes = []

        def recursive_search(node):
            if node is None:
                return

            pm_node = pm.PyNode(node)

            for child in pm.listRelatives(node, c=1):
                if child is None:
                    continue
                else:
                    pm_child = pm.PyNode(child)
                    new_item = None

                    if pm.nodeType(child) == "transform" and len(pm.listRelatives(child, typ=light_types)) == 0:
                        new_item = self.create_group(str(child), str(node), True)

                    elif pm.nodeType(child) == "transform" and len(pm.listRelatives(child, typ=light_types)) > 0:
                        new_item = self.create_light(str(child.getShape()).replace("Shape", ""), node)

                    if new_item is not None:
                        all_nodes.append(new_item)

                    recursive_search(child)

        recursive_search("l_rig")

        for n in all_nodes:
            if n.pm_node.getParent() != "l_rig":
                for i in all_nodes:
                    if n.pm_node.getParent() == i.pm_node:
                        self.invisibleRootItem().removeChild(n)
                        i.addChild(n)

                        n.create_widgets()

                        for column, widget in n.widget_data.items():
                            self.setItemWidget(n, column, widget)


class ConsoleWidget(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)

    def __init__(self, *args, **kwargs):
        super(ConsoleWidget, self).__init__(*args, **kwargs)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.setContentsMargins(0, 0, 0, 0)

    def create_actions(self):
        pass

    def create_widgets(self):
        self.console_header_lbl = MWidgets.HeaderLabel("Console")

        self.console_tw = LightConsoleTreeWidget()

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.addWidget(self.console_header_lbl)
        main_layout.addWidget(self.console_tw)

    def create_connections(self):
        self.console_tw.log_event.connect(self.push_console_tw_log)

    def push_console_tw_log(self, log_type, log_message):
        self.log_event.emit(log_type, log_message)

    def create_light(self, light):
        self.console_tw.create_light(light, "l_rig")
        self.log_event.emit("result", "Created " + light)
        pass
