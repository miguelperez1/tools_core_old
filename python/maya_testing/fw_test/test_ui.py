import os
import logging
import json

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import pymel.core as pm

from pyqt_commons import MWidgets

logger = logging.getLogger(__name__)
logger.setLevel(10)


class ExampleDialog(QtWidgets.QMainWindow):
    def __init__(self, parent=MWidgets.maya_main_window()):
        super(ExampleDialog, self).__init__(parent)

        self.setWindowTitle("Window")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.setObjectName("ExampleDialog")

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        data = {
            "test_key": "test_value"
        }

        fp = r"C:\Users\migue\Documents\test.json"

        with open(fp, 'w') as outfile:
            json.dump(data, outfile)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.path_le = QtWidgets.QLineEdit()
        self.run_btn = QtWidgets.QPushButton("go")

    def create_layout(self):
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)
        main_layout.addWidget(self.path_le)
        main_layout.addWidget(self.run_btn)

    def create_connections(self):
        self.run_btn.clicked.connect(self.run_callback)

    def run_callback(self):
        self.fw = QtCore.QFileSystemWatcher([self.path_le.text()])
        self.fw.fileChanged.connect(self.notify)

    def notify(self):
        f = open(self.path_le.text())
        data = json.load(f)

        print(data)


def main():
    try:
        cmds.deleteUI("ExampleDialog")
    except Exception:
        pass

    dialog = ExampleDialog()
    dialog.show()


if __name__ == "__main__":
    main()
