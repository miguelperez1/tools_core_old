from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds

from pyqt_commons import MWidgets
from maya_core.asset_manager.library_utils import constants
from maya_core.asset_browser import AssetBrowserWidget

LIBRARIES = constants.libraries


class AssetBrowser(QtWidgets.QMainWindow):
    def __init__(self, parent=MWidgets.maya_main_window()):
        super(AssetBrowser, self).__init__(parent)

        self.setWindowTitle("Asset Browser")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.setObjectName("AssetBrowserUI")
        self.setMinimumSize(1560, 877)

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.asset_browser_widget = AssetBrowserWidget.AssetBrowserWidget(1560-20, 877-20)

    def create_layout(self):
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)
        main_layout.addWidget(self.asset_browser_widget)

    def create_connections(self):
        pass


def main():
    try:
        cmds.deleteUI("AssetBrowserUI")
    except Exception:
        pass

    dialog = AssetBrowser()
    dialog.show()


if __name__ == "__main__":
    main()
