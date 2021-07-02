from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds

from pyqt_commons import MWidgets
from maya_core.lookdev.material_builder_ui import MaterialBuilderWidget
from maya_core.lookdev.material_utils import material_utils

reload(MaterialBuilderWidget)


class MaterialBuilderUI(QtWidgets.QMainWindow):
    def __init__(self, parent=MWidgets.maya_main_window()):
        super(MaterialBuilderUI, self).__init__(parent)

        self.setWindowTitle("Material Builder")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.setObjectName("MaterialBuilderUI")
        self.setMinimumSize(650, 500)

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.material_builder_widget = MaterialBuilderWidget.MaterialBuilderWidget(self.width(), self.height())

        self.build_btn = QtWidgets.QPushButton("Build")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")

    def create_layout(self):
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)
        m = 20
        main_layout.setContentsMargins(m, m, m, m)
        main_layout.addWidget(self.material_builder_widget)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.build_btn)
        btn_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(btn_layout)

    def create_connections(self):
        self.build_btn.clicked.connect(self.build_material)
        self.cancel_btn.clicked.connect(self.close)

    def build_material(self):
        material_data = self.material_builder_widget.get_material_data()

        if material_data['name']:
            material = material_utils.build_material(material_data)
            print material


def main():
    try:
        cmds.deleteUI("MaterialBuilderUI")
    except Exception:
        pass

    dialog = MaterialBuilderUI()
    dialog.show()


if __name__ == "__main__":
    main()
