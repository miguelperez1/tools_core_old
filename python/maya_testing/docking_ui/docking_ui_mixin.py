from shiboken2 import getCppPointer

import maya.cmds as cmds
import maya.mel as mel
from maya.OpenMayaUI import MQtUtil
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui


# Order matters in multiple inheritance
class DockableButton(MayaQWidgetDockableMixin, QtWidgets.QWidget):

    object_name = 'DockableUI'

    def __init__(self):
        super(DockableButton, self).__init__()

        # No need to parent to maya window
        # Parented by default to maya workspace widget
        self.setWindowTitle("Dockable Button")
        self.objectName(self.object_name)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

        workspace_control_name = "{}WorkspaceControl".format(self.object_name)

        if cmds.workspaceControl(workspace_control_name, q=True, exists=True):
            workspace_control_pointer = long(MQtUtil.findControl(workspace_control_name))
            widget_pointer = long(getCppPointer(self)[0])

            MQtUtil.addWidgetToMayaLayout(widget_pointer, workspace_control_pointer)

    def create_actions(self):
        pass

    def create_widgets(self):
        self.button = QtWidgets.QPushButton()

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.addWidget(self.button)
        main_layout.addStretch()

    def create_connections(self):
        pass


def main():
    try:
        if ui and ui.parent():
            workspace_control_name = ui.parent().objectName()

            if cmds.window(workspace_control_name, exist=True):
                cmds.deleteUI(workspace_control_name)
    except Exception:
        pass

    ui = DockableButton()

    workspace_control_name = "{}WorkspaceControl".format(ui.objectName())

    ui_script = "from maya_testing.docking_ui import docking_ui\nui = DockableButton('{0}')".format(workspace_control_name)

    ui.show(dockable=True, uiScript=ui_script)


if __name__ == '__main__':
    main()
