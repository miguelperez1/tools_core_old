from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds

from pyqt_commons import MWidgets


class ExampleDialog(QtWidgets.QMainWindow):
    def __init__(self, parent=MWidgets.maya_main_window()):
        super(ExampleDialog, self).__init__(parent)

        self.setWindowTitle("Window")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.setObjectName("ExampleDialog")

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
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)

    def create_menu(self):
        self.menu_bar = QtWidgets.QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        file_menu = QtWidgets.QMenu("File", self)
        edit_menu = QtWidgets.QMenu("Edit", self)
        tools_menu = QtWidgets.QMenu("Tools", self)
        help_menu = QtWidgets.QMenu("Help", self)

        self.menu_bar.addMenu(file_menu)
        self.menu_bar.addMenu(edit_menu)
        self.menu_bar.addMenu(tools_menu)
        self.menu_bar.addMenu(help_menu)

    def create_connections(self):
        pass

    def create_script_jobs(self):
        pass

    def on_dag_object_created(self):
        if len(cmds.ls(type="light")) != len(self.light_items):
            self.refresh_lights()

    def delete_script_jobs(self):
        for job in self.script_jobs:
            cmds.scriptJob(kill=job)

        self.script_jobs = []

    def refresh_lights(self):
        pass

    def showEvent(self, event):
        self.create_script_jobs()

    def closeEvent(self, event):
        self.delete_script_jobs()


def main():
    try:
        dialog.close()
        dialog.deleteLater()
    except:
        pass

    dialog = ExampleDialog()
    dialog.show()


if __name__ == "__main__":
    main()
