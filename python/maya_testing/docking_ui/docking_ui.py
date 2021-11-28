from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds

from pyqt_commons import DockableWidget



class ProjectToolsUI(DockableWidget.DockableWidget):
    WINDOW_TITLE = "Project Tools"

    def __init__(self):
        super(ProjectToolsUI, self).__init__()

        self.setMinimumWidth(400)

    def create_actions(self):
        pass

    def create_widgets(self):
        self.project_label = QtWidgets.QLabel("Project Tools")

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.addWidget(self.project_label)

    def create_connections(self):
        pass


def main():
    workspace_contorl_name = ProjectToolsUI.get_workspace_control_name()
    if cmds.workspaceControl(workspace_contorl_name, q=True, exists=True):
        cmds.deleteUI(workspace_contorl_name)

    ProjectToolsUI.module_name_override = "docking_ui"
    ui = ProjectToolsUI()


if __name__ == '__main__':
    main()
