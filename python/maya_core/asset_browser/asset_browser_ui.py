import logging

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds

from pyqt_commons import MWidgets
from pyqt_commons import DockableWidget

from maya_core.asset_manager.library_utils import constants
from maya_core.asset_browser import AssetBrowserWidget

LIBRARIES = constants.libraries

logger = logging.getLogger(__name__)
logger.setLevel(10)

class AssetBrowser(DockableWidget.DockableWidget):
    WINDOW_TITLE = "Asset Browser"

    def __init__(self):
        super(AssetBrowser, self).__init__()

        self.setWindowTitle("Asset Browser")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.setObjectName("AssetBrowserUI")

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.asset_browser_widget = AssetBrowserWidget.AssetBrowserWidget(1920, 0)

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.asset_browser_widget)

    def create_connections(self):
        pass


def main():
    workspace_contorl_name = AssetBrowser.get_workspace_control_name()
    if cmds.workspaceControl(workspace_contorl_name, q=True, exists=True):
        cmds.deleteUI(workspace_contorl_name)

    AssetBrowser.module_name_override = "asset_browser_ui"
    ui = AssetBrowser()


if __name__ == "__main__":
    main()
