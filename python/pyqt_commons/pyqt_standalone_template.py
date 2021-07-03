"""
this is the maya client

"""

import os
import sys
import json
import socket

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

# Connect to Maya with sockets
BUFFER_SIZE = 4096
PORT = 20201
maya_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
maya_socket.connect(("localhost", PORT))


class AssetBrowser(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(AssetBrowser, self).__init__(parent)

        self.setWindowTitle("Window")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.setFixedSize(1200, 700)

        self.setObjectName("ExampleDialog")

        self.current_asset = None

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        pass

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)

    def create_connections(self):
        pass


def main():
    app = QtWidgets.QApplication(sys.argv)
    browser = AssetBrowser()
    browser.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
