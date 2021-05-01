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


def convert_K_to_RGB(colour_temperature):
    """
    Converts from K to RGB, algorithm courtesy of
    http://www.tannerhelland.com/4435/convert-temperature-rgb-algorithm-code/
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


class LightConsoleTreeWidget(QtWidgets.QTreeWidget):
    log_event = QtCore.Signal(str, str)

    def __init__(self, *args, **kwargs):
        super(LightConsoleTreeWidget, self).__init__(*args, **kwargs)

        self.light_icons = {
            "VRayLightRectShape": "C:\\Program Files\\Autodesk\\Maya2020\\vray\\icons\\shelf_LightRect_200.png",
            "VRayLightSphereShape": "C:\\Program Files\\Autodesk\\Maya2020\\vray\\icons\\shelf_LightSphere_200.png",
            "VRayLightDomeShape": "C:\\Program Files\\Autodesk\\Maya2020\\vray\\icons\\shelf_LightDome_200.png",
            "directionalLight": ":/directionallight.png",
        }

        self.header_item = QtWidgets.QTreeWidgetItem(
            ["Enabled", "", "Name", "Exposure", "Color", 'Temperature', "Tex", "Directional", 'Angle', 'Invisible', ''])
        self.setHeaderItem(self.header_item)

        self.setAlternatingRowColors(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.setColumnWidth(2, 250)
        self.setColumnWidth(3, 100)
        self.setColumnWidth(4, 150)
        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)

        self.itemDoubleClicked.connect(self.onTreeWidgetItemDoubleClicked)
        self.itemSelectionChanged.connect(self.select_light)
        self.itemChanged.connect(self.update_attribute)

        self.prev_attr_value = None

    def onTreeWidgetItemDoubleClicked(self, item, column):
        if self.can_edit_column(item, column):
            self.prev_attr_value = item.text(column)

            self.editItem(item, column)

    def update_attribute(self, item, column, value=None):
        if item.text(2) == "":
            return

        attribute = self.header_item.text(column).lower()

        if value is None:
            value = item.text(column)
        else:
            value = value

        if self.prev_attr_value is None:
            return

        # Needs to go here
        if attribute == "name":
            try:
                cmds.rename(self.prev_attr_value, value)
            except Exception:
                self.log_event.emit("error", "illegal characters in name")
                item.setText(column, self.prev_attr_value)
                return

        light_name = item.text(2)
        light_shape = cmds.listRelatives(light_name, shapes=True)[0]
        light_type = item.data(0, QtCore.Qt.UserRole)

        # Set attribute on light_shape

        # Exposure
        if attribute == "exposure":
            intensity = pow(2, float(value))
            cmds.setAttr("{}.intensity".format(light_shape), intensity)
            item.setText(3, "{:.2f}".format(float(value)))

        # Directional
        if attribute == "directional" and light_type == "VRayLightRectShape":
            cmds.setAttr("{}.directional".format(light_shape), float(value))
            item.setText(7, "{:.3f}".format(float(value)))

        # Angle
        if attribute == "angle" and light_type == "directionalLight":
            cmds.setAttr("{}.lightAngle".format(light_shape), float(value))
            item.setText(8, "{:.3f}".format(float(value)))

        if attribute == "temperature":
            color_btn_widget = self.itemWidget(item, 4).layout().itemAt(1).widget()

            color = convert_K_to_RGB(int(value))

            color_btn_widget.set_button_color(color, 1)

    def can_edit_column(self, item, column):
        light_type = item.data(0, QtCore.Qt.UserRole)

        column_editability = {
            "VRayLightRectShape": [2, 3, 4, 5, 7],
            "VRayLightSphereShape": [2, 3, 4, 5],
            "VRayLightDomeShape": [2, 3, 4, 5],
            "directionalLight": [2, 3, 4, 5, 8]
        }

        if column in column_editability[light_type]:
            return True
        return False

    def create_light(self, light_type, light_name):
        # Get the light shape
        light_shape = cmds.listRelatives(light_name, shapes=True)[0]

        size = 35

        new_light_item = QtWidgets.QTreeWidgetItem()
        new_light_item.setSizeHint(0, QtCore.QSize(size, size))
        new_light_item.setFlags(new_light_item.flags() | QtCore.Qt.ItemIsEditable)
        new_light_item.setData(0, QtCore.Qt.UserRole, light_type)

        # Set Attributes from source
        # Enabled
        enabled_cb = QtWidgets.QCheckBox()

        if light_type != "directionalLight":
            enabled_cb.setChecked(cmds.getAttr("{}.enabled".format(light_shape)))
        else:
            enabled_cb.setChecked(cmds.getAttr("{}.visibility".format(light_shape)))

        # Icon
        light_icon = MWidgets.PreviewLabel()
        light_icon.set_image(self.light_icons[light_type], size)

        # Name
        new_light_item.setText(2, light_name)

        # Exposure
        current_intensity = cmds.getAttr("{}.intensity".format(light_shape))
        exposure = math.log(current_intensity)

        exposure_str = '{:.2f}'.format(exposure)

        new_light_item.setText(3, exposure_str)

        # Color
        color_cw = QtWidgets.QWidget()

        color_widget = MWidgets.ColorPickerTreeWidgetItemWidget(120, size * .75, str(light_name), new_light_item)
        color_widget.setObjectName("color_widget")

        color_widget.clicked_event.connect(self.reset_temp)
        # color_widget = MWidgets.CustomColorButton()

        color_layout = QtWidgets.QHBoxLayout(color_cw)
        color_layout.addStretch()
        color_layout.addWidget(color_widget)
        color_layout.addStretch()

        # color_widget.color_changed.connect(self.update_color)

        # Temperature
        new_light_item.setText(5, "6500")

        # Tex

        # Directional
        if light_type == "VRayLightRectShape":
            directionality = cmds.getAttr("{}.directional".format(light_shape))
            directionality_str = '{:.3f}'.format(directionality)

            new_light_item.setText(7, directionality_str)

        # Light Angle
        if light_type == "directionalLight":
            angle = cmds.getAttr("{}.lightAngle".format(light_shape))
            angle_str = '{:.3f}'.format(angle)

            new_light_item.setText(8, angle_str)

        # Invisible

        if light_type != "directionalLight":
            invisible_cw = QtWidgets.QWidget()
            invisible_cb = QtWidgets.QCheckBox()

            invisible_cb.setChecked(cmds.getAttr("{}.invisible".format(light_shape)))

            invisible_layout = QtWidgets.QHBoxLayout(invisible_cw)
            invisible_layout.addWidget(invisible_cb)

        self.addTopLevelItem(new_light_item)

        # Set Widgets
        self.setItemWidget(new_light_item, 0, enabled_cb)
        self.setItemWidget(new_light_item, 1, light_icon)
        self.setItemWidget(new_light_item, 4, color_cw)

        if light_type != "directionalLight":
            self.setItemWidget(new_light_item, 9, invisible_cw)

        # return
        for col in range(9):
            if col == 2:
                continue
            new_light_item.setTextAlignment(col, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        self.resizeColumnToContents(4)
        self.resizeColumnToContents(9)

    def select_light(self):

        selection = []
        for i in self.selectedItems():
            selection.append(i.text(2))
        cmds.select(selection)

    def update_color(self, color):
        self.log_event.emit("result", color)

    def reset_temp(self, item):
        self.update_attribute(item, 5, 6500, 0)


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

    def create_light(self, type, name):
        self.console_tw.create_light(type, name)
        self.log_event.emit("result", "Created " + name)
        pass
