import os
import logging

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds

from pyqt_commons import MWidgets
from pyqt_commons import DockableWidget
from maya_core.pipeline.project import maya_project

reload(MWidgets)
reload(maya_project)

projects_root = r"F:\share\projects"

logger = logging.getLogger(__name__)
logger.setLevel(10)


class ProjectToolsUI(DockableWidget.DockableWidget):
    WINDOW_TITLE = "Project Tools"

    def __init__(self):
        self.maya_project = maya_project.get_current_project()

        super(ProjectToolsUI, self).__init__()

        self.setContentsMargins(20, 20, 20, 20)

    def create_actions(self):
        pass

    def create_widgets(self):
        file_browse_icon = QtGui.QIcon(':fileOpen.png')

        self.project_hdrlbl = MWidgets.HeaderLabel("Project Tools", 1.5)

        self.projects_lbl = MWidgets.HeaderLabel("Project: ")
        self.projects_cmbx = QtWidgets.QComboBox()
        self.projects_cmbx.setMinimumWidth(150)

        self.projects_open_btn = QtWidgets.QPushButton()
        self.projects_open_btn.setIcon(file_browse_icon)

        self.create_project_lble = MWidgets.LabeledLineEdit("Project Name: ")

        self.create_project_btn = QtWidgets.QPushButton("Create")

        self.seq_lbl = QtWidgets.QLabel("Sequence: ")
        self.seq_cmbx = QtWidgets.QComboBox()
        self.seq_create_btn = QtWidgets.QPushButton("Create")

        self.shot_lbl = QtWidgets.QLabel("Shot: ")
        self.shot_cmbx = QtWidgets.QComboBox()
        self.shot_create_btn = QtWidgets.QPushButton("Create")

        self.open_shot_btn = QtWidgets.QPushButton()
        self.open_shot_btn.setIcon(file_browse_icon)

        self.refresh_projects()

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        header_layout = QtWidgets.QVBoxLayout()

        header_layout.addWidget(self.project_hdrlbl)
        header_layout.addWidget(MWidgets.QHLine())
        # header_layout.addWidget(MWidgets.VSpacerWidget(25))

        main_layout.addLayout(header_layout)

        inner_layout = QtWidgets.QVBoxLayout()
        inner_layout.setContentsMargins(25, 15, 0, 0)

        set_layout = QtWidgets.QHBoxLayout()
        set_layout.addWidget(self.projects_lbl)
        set_layout.addWidget(self.projects_cmbx)
        set_layout.addWidget(self.projects_open_btn)
        set_layout.addStretch()

        inner_layout.addLayout(set_layout)
        inner_layout.addWidget(MWidgets.QHLine())

        shot_seq_layout = QtWidgets.QHBoxLayout()
        shot_seq_layout.addWidget(self.seq_lbl)
        shot_seq_layout.addWidget(self.seq_cmbx)
        shot_seq_layout.addWidget(self.seq_create_btn)
        shot_seq_layout.addWidget(self.shot_lbl)
        shot_seq_layout.addWidget(self.shot_cmbx)
        shot_seq_layout.addWidget(self.shot_create_btn)
        shot_seq_layout.addWidget(self.open_shot_btn)
        shot_seq_layout.addStretch()

        inner_layout.addLayout(shot_seq_layout)

        create_layout = QtWidgets.QHBoxLayout()
        create_layout.addWidget(self.create_project_lble)
        create_layout.addWidget(self.create_project_btn)

        main_layout.addLayout(inner_layout)
        main_layout.addStretch()
        main_layout.addLayout(create_layout)

    def create_connections(self):
        self.projects_cmbx.currentTextChanged.connect(self.set_project)
        self.create_project_btn.clicked.connect(self.create_btn_callback)
        self.projects_open_btn.clicked.connect(self.open_project_root)

    def open_project_root(self):
        os.startfile(self.maya_project.project_root)

    def create_btn_callback(self):
        self.projects_cmbx.blockSignals(True)
        if self.create_project_lble.text():
            self.maya_project = maya_project.Project(self.create_project_lble.text())
            self.maya_project.create_maya_project()
            self.refresh_projects()
        self.projects_cmbx.blockSignals(False)

    def set_project(self):
        project_root = os.path.join(projects_root, self.projects_cmbx.currentText())

        maya_project.set_maya_project(project_root)
        self.maya_project = maya_project.get_current_project()

        self.refresh_seq()

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
            self.maya_project = maya_project.Project(current_project)

        self.refresh_seq()

        self.projects_cmbx.blockSignals(False)

    def refresh_seq(self):
        self.seq_cmbx.blockSignals(True)
        self.seq_cmbx.clear()

        # replace this with sequences manifest
        for seq in sorted(os.listdir(self.maya_project.seq_root)):
            self.seq_cmbx.addItem(seq)

        self.seq_cmbx.setCurrentIndex(0)

        self.seq_cmbx.blockSignals(False)

        self.refresh_shots()

    def refresh_shots(self):
        self.shot_cmbx.blockSignals(True)
        self.shot_cmbx.clear()

        if self.seq_cmbx.currentText():
            # change this to get from sequence manifest
            for shot in os.listdir(os.path.join(self.maya_project.seq_root, self.seq_cmbx.currentText())):
                self.shot_cmbx.addItem(shot)

        self.shot_cmbx.blockSignals(False)


def main():
    workspace_contorl_name = ProjectToolsUI.get_workspace_control_name()
    if cmds.workspaceControl(workspace_contorl_name, q=True, exists=True):
        cmds.deleteUI(workspace_contorl_name)

    ProjectToolsUI.module_name_override = "project_tools_ui"
    ui = ProjectToolsUI()


if __name__ == "__main__":
    main()
