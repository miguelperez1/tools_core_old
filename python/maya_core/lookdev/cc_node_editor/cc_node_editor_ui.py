import re

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import pymel.core as pm

from pyqt_commons import MWidgets
from maya_core.common_tools.maya_utilities import maya_utilities as mu


class CCEditorUI(QtWidgets.QMainWindow):
    def __init__(self, parent=MWidgets.maya_main_window()):
        super(CCEditorUI, self).__init__(parent)

        self.setWindowTitle("CC Node Finder")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.setObjectName("CCEditorUI")
        self.setMinimumSize(500, 400)

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.search_lble = MWidgets.LabeledLineEdit("Search: ")

        self.refresh_btn = QtWidgets.QPushButton()
        self.refresh_btn.setIcon(QtGui.QIcon(r"F:\share\tools\shelf_icons\reload.png"))

        self.mat_tw = QtWidgets.QTreeWidget()
        self.mat_tw.setHeaderHidden(True)

        self.refresh_mats()

    def create_layout(self):
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)

        search_layout = QtWidgets.QHBoxLayout()
        search_layout.addWidget(self.search_lble)
        search_layout.addWidget(self.refresh_btn)

        main_layout.addLayout(search_layout)

        main_layout.addWidget(self.mat_tw)

    def create_connections(self):
        self.refresh_btn.clicked.connect(self.refresh_mats)
        self.search_lble.le_widget.textChanged.connect(self.refresh_mats)
        self.mat_tw.itemSelectionChanged.connect(self.mat_tw_selection_callback)


    def refresh_mats(self):
        self.mat_tw.blockSignals(True)
        self.mat_tw.clear()

        for mat in mu.get_all_materials():
            mat_item = QtWidgets.QTreeWidgetItem()
            mat_item.setText(0, str(mat))

            ccs = mu.filter_connected_nodes(mat, "colorCorrect")

            for cc in ccs:
                if not re.search(self.search_lble.text(), str(cc)) and not re.search(self.search_lble.text(), str(mat)):
                    continue

                cc_item = QtWidgets.QTreeWidgetItem()
                cc_item.setText(0, str(cc))

                mat_item.addChild(cc_item)

            self.mat_tw.addTopLevelItem(mat_item)

        self.mat_tw.blockSignals(False)

    def mat_tw_selection_callback(self):
        for item in self.mat_tw.selectedItems():
            if pm.nodeType(item.text(0)) == "colorCorrect":
                pm.select(item.text(0))


def main():
    try:
        cmds.deleteUI("CCEditorUI")
    except Exception:
        pass

    dialog = CCEditorUI()
    dialog.show()


if __name__ == "__main__":
    main()
