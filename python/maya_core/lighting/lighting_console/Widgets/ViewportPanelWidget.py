from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import vray
import maya.OpenMayaUI as mui
import shiboken2

from pyqt_commons import MWidgets

from maya_core.lighting.lighting_console.constants import *


def get_display_flags(model):
    display_flags = {}

    for l in pm.modelEditor(model, q=True, sts=True).split("\n"):
        line = l.lstrip()
        if line.startswith("-"):
            flag = line[1:].split(" ")[0]
            value = " ".join(line[1:].split(" ")[1:])

            display_flags[flag] = value

    return display_flags


def set_display_flags(model, display_flags):
    for flag, value, in display_flags.items():
        mel_command = "modelEditor -e -{0} {1} {2}".format(flag, value, model)
        try:
            mel.eval(mel_command)
            print(mel_command)
        except Exception as e:
            print(e)


class ViewportPanelWidget(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)

    def __init__(self, *args, **kwargs):
        super(ViewportPanelWidget, self).__init__(*args, **kwargs)

        self.setObjectName("ViewportPanelWidget")

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setObjectName("ViewportPanelWidgetLayout")

        self.create_viewport_panel()

    def create_viewport_panel(self):
        cmds.setParent("ViewportPanelWidgetLayout")
        paneLayoutName = cmds.paneLayout()
        modelPanelName = cmds.modelPanel("embeddedModelPanel#", cam="shotCam")

        ptr = mui.MQtUtil.findControl(paneLayoutName)
        paneLayoutQt = shiboken2.wrapInstance(long(ptr), QtWidgets.QWidget)

        display_flags = get_display_flags(modelPanelName)

        for key in display_flags.keys():
            try:
                float(display_flags[key])
                display_flags[key] = 0
            except Exception:
                pass

        display_flags["polymeshes"] = 1
        display_flags["displayAppearance"] = "smoothShaded"
        display_flags["displayTextures"] = 1
        display_flags["headsUpDisplay"] = 1
        display_flags["selectionHiliteDisplay"] = 1

        set_display_flags(modelPanelName, display_flags)

        self.main_layout.addWidget(paneLayoutQt)
