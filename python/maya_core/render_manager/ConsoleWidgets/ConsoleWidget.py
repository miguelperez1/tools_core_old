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

SCALE = 1
RES_X = 2550 * SCALE
RES_Y = 1320 * SCALE


class LightConsoleTreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, light_type, *args, **kwargs):
        super(LightConsoleTreeWidgetItem, self).__init__(*args, **kwargs)

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


class LightConsoleTreeWidget(QtWidgets.QTreeWidget):
    def __init__(self, *args, **kwargs):
        super(LightConsoleTreeWidget, self).__init__(*args, **kwargs)

        self.light_icons = {
            "VRayLightRectShape": "C:\\Program Files\\Autodesk\\Maya2020\\vray\\icons\\shelf_LightRect_200.png",
            "VRayLightSphereShape": "C:\\Program Files\\Autodesk\\Maya2020\\vray\\icons\\shelf_LightSphere_200.png",
            "VRayLightDomeShape": "C:\\Program Files\\Autodesk\\Maya2020\\vray\\icons\\shelf_LightDome_200.png",
            "directionalLight": ":/directionallight.png",
        }

        self.header_item = QtWidgets.QTreeWidgetItem(
            ["Enabled", "", "Name", "Exposure", "Color", 'Temperature', "Tex", "Directional", 'Angle', 'Invisible'])
        self.setHeaderItem(self.header_item)

        self.setAlternatingRowColors(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.setColumnWidth(2, 250)
        self.setColumnWidth(3, 100)
        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)

        self.itemDoubleClicked.connect(self.onTreeWidgetItemDoubleClicked)
        self.itemChanged.connect(self.update_attribute)
        self.itemSelectionChanged.connect(self.select_light)

    def onTreeWidgetItemDoubleClicked(self, item, column):
        if self.can_edit_column(item, column):
            self.prev_light_name = item.text(2)
            print self.prev_light_name
            self.editItem(item, column)

    def update_attribute(self, item, column):
        attribute = self.header_item.text(column).lower()
        value = item.text(column)

        if attribute == "name":
            cmds.rename(self.prev_light_name, item.text(2))

        light_name = item.text(2)
        light_shape = cmds.listRelatives(light_name, shapes=True)[0]

        if attribute == "exposure":
            cmds.setAttr("{0}.intensity".format(light_shape), pow(2, float(value)))
            item.setText(column, "{:.2f}".format((round(float(value), 2))))
        elif attribute == "temperature":
            pass
        elif attribute == "directional":
            cmds.setAttr("{0}.directional".format(light_shape), float(value))
            item.setText(column, "{:.3f}".format((round(float(value), 3))))
        elif attribute == "angle":
            cmds.setAttr("{0}.lightAngle".format(light_shape), float(value))
            item.setText(column, "{:.3f}".format((round(float(value), 3))))

    def can_edit_column(self, item, column):
        light_type = item.data(0, QtCore.Qt.UserRole)

        column_editability = {
            "VRayLightRectShape": [2, 3, 5, 7],
            "VRayLightSphereShape": [2, 3, 5],
            "VRayLightDomeShape": [2, 3, 5],
            "directionalLight": [2, 3, 5, 8]
        }

        if column in column_editability[light_type]:
            return True
        return False

    def create_light(self, light_type, light_name):
        light_shape = cmds.listRelatives(light_name, shapes=True)[0]

        size = 35
        new_item = QtWidgets.QTreeWidgetItem()
        new_item.setText(2, light_name)
        new_item.setSizeHint(0, QtCore.QSize(size, size))
        new_item.setFlags(new_item.flags() | QtCore.Qt.ItemIsEditable)
        new_item.setData(0, QtCore.Qt.UserRole, light_type)

        icon = MWidgets.PreviewLabel()
        icon.set_image(self.light_icons[light_type], size)

        enabled_cb = QtWidgets.QCheckBox()
        enabled_cb.setChecked(True)

        self.addTopLevelItem(new_item)

        self.setItemWidget(new_item, 0, enabled_cb)
        self.setItemWidget(new_item, 1, icon)

        cmds.setAttr("{}.intensity".format(light_shape), 1)

        exposure = math.log(cmds.getAttr("{}.intensity".format(light_shape)))

        if light_type == "VRayLightRectShape":
            directional = cmds.getAttr("{}.directional".format(light_shape))
            new_item.setText(7, "{:.3f}".format((round(float(directional), 3))))

        new_item.setText(3, "{:.2f}".format((round(float(exposure), 2))))

        if light_type != "directionalLight":
            cmds.setAttr("{}.invisible".format(light_shape), 1)
            invisible_cb = QtWidgets.QCheckBox()
            invisible_cb.setChecked(cmds.getAttr("{}.invisible".format(light_shape)))

            self.setItemWidget(new_item, 9, invisible_cb)

        if light_type == "directionalLight":
            angle = cmds.getAttr("{}.lightAngle".format(light_shape))
            new_item.setText(8, "{:.3f}".format((round(float(angle), 3))))

        new_item.setText(3, "{:.2f}".format((round(float(exposure), 2))))

        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)

    def select_light(self):

        selection = []
        for i in self.selectedItems():
            selection.append(i.text(2))
        cmds.select(selection)


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
        pass

    def create_light(self, type, name):
        self.console_tw.create_light(type, name)
        self.log_event.emit("result", "Created " + name)
        pass
