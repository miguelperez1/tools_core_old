from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import maya.cmds as cmds

from maya_core.common_tools import logger
from maya_core.asset_manager.asset_browser import AssetBrowser

reload(AssetBrowser)

log = logger.Logger()


def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class AssetBrowserWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=maya_main_window()):
        super(AssetBrowserWindow, self).__init__(parent)

        self.setWindowTitle("Asset Browser")
        self.setObjectName("AssetBrowserUI")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.setFixedSize(950 * 1.25, 890 * 1.25)

        self.setWindowFlags(
            self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.asset_browser_wdg = AssetBrowser.AssetBrowser(parent=self)

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)
        main_layout.addWidget(self.asset_browser_wdg)

    def create_connections(self):
        pass


def main():
    try:
        cmds.deleteUI("AssetBrowserUI")
    except Exception:
        pass

    asset_browser = AssetBrowserWindow()
    asset_browser.show()


if __name__ == "__main__":
    main()
