from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import pymel.core as pm
import vray

from pyqt_commons import MWidgets

reload(MWidgets)

from maya_core.lighting_console.constants import *

from maya_core.common_tools.logger import Logger


class LogWidget(object):
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
