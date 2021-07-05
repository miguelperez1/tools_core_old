import os
import logging

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds

from pyqt_commons import MWidgets
from maya_core.pipeline.project import maya_project

reload(maya_project)

projects_root = r"F:\share\projects"

logger = logging.getLogger(__name__)
logger.setLevel(10)


class ProjectToolsUI(QtWidgets.QMainWindow):
    def __init__(self, parent=MWidgets.maya_main_window()):
        super(ProjectToolsUI, self).__init__(parent)

        self.setWindowTitle("Project Tools")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(500)

        self.setObjectName("ProjectToolsUI")

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.projects_lbl = QtWidgets.QLabel("Project: ")
        self.projects_cmbx = QtWidgets.QComboBox()
        self.projects_cmbx.setMinimumWidth(150)

        self.refresh_projects()

        self.create_project_lble = MWidgets.LabeledLineEdit("Project Name:")

        self.create_btn = QtWidgets.QPushButton("Create")

    def create_layout(self):
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)

        set_layout = QtWidgets.QHBoxLayout()
        set_layout.addWidget(self.projects_lbl)
        set_layout.addWidget(self.projects_cmbx)
        set_layout.addStretch()

        main_layout.addLayout(set_layout)
        main_layout.addWidget(MWidgets.QHLine())

        create_layout = QtWidgets.QHBoxLayout()
        create_layout.addWidget(self.create_project_lble)
        create_layout.addWidget(self.create_btn)

        main_layout.addLayout(create_layout)
        main_layout.addStretch()

    def create_connections(self):
        self.projects_cmbx.currentTextChanged.connect(self.set_project)
        self.create_btn.clicked.connect(self.create_btn_callback)

    def create_btn_callback(self):
        self.projects_cmbx.blockSignals(True)
        if self.create_project_lble.text():
            maya_project.create_maya_project(self.create_project_lble.text())
            self.refresh_projects()
        self.projects_cmbx.blockSignals(False)

    def set_project(self):
        project_root = os.path.join(projects_root, self.projects_cmbx.currentText())

        maya_project.set_maya_project(project_root)

    def refresh_projects(self):
        self.projects_cmbx.blockSignals(True)
        self.projects_cmbx.clear()

        for project in os.listdir(projects_root):
            if project == 'archive' or not os.path.isdir(os.path.join(projects_root, project)):
                continue

            self.projects_cmbx.addItem(project)

        current_project = cmds.workspace(sn=1).split("/")[-1]

        if current_project in os.listdir(projects_root):
            self.projects_cmbx.setCurrentText(current_project)

        self.projects_cmbx.blockSignals(False)


def main():
    try:
        cmds.deleteUI("ProjectToolsUI")
    except Exception:
        pass

    dialog = ProjectToolsUI()
    dialog.show()


if __name__ == "__main__":
    main()
