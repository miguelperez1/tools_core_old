from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import maya.cmds as cmds

import os
import sys
import subprocess


def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class ExampleDialog(QtWidgets.QDialog):
    """
    Dialog used to demonstrates many of the standard dialogs available in Qt
    """

    def __init__(self, parent=maya_main_window()):
        super(ExampleDialog, self).__init__(parent)

        self.setWindowTitle("Window")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        pass

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)

    def create_connections(self):
        pass


if __name__ == "__main__":

    try:
        dialog.close()
        dialog.deleteLater()
    except:
        pass

    dialog = ExampleDialog()
    dialog.show()
