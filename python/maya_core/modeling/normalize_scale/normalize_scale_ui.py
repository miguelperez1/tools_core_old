from PySide2 import QtCore
from PySide2 import QtWidgets

import pymel.core as pm
import maya.cmds as cmds

from pyqt_commons import MWidgets
from maya_core.modeling.normalize_scale import normalize_scale

class NormalizeScaleUI(QtWidgets.QMainWindow):
    def __init__(self, parent=MWidgets.maya_main_window()):
        super(NormalizeScaleUI, self).__init__(parent)

        self.setWindowTitle("Normalize Scale")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.setObjectName("NormalizeScaleUI")
        self.setMinimumSize(400, 70)

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.scale_lbl = QtWidgets.QLabel("Scale: ")
        self.scale_le = QtWidgets.QLineEdit()

        self.axis_lbl = QtWidgets.QLabel("Axis: ")
        self.axis_cmbx = QtWidgets.QComboBox()
        self.axis_cmbx.addItems(['x', 'y', 'z'])
        self.axis_cmbx.setCurrentIndex(1)

        self.ok_btn = QtWidgets.QPushButton("Scale")

    def create_layout(self):
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)

        scale_layout = QtWidgets.QHBoxLayout()
        scale_layout.addWidget(self.scale_lbl)
        scale_layout.addWidget(self.scale_le)
        scale_layout.addWidget(self.axis_lbl)
        scale_layout.addWidget(self.axis_cmbx)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)

        main_layout.addLayout(scale_layout)
        main_layout.addLayout(btn_layout)

    def create_connections(self):
        self.ok_btn.clicked.connect(self.normalize_scale)

    def normalize_scale(self):
        selection = pm.ls(sl=1)

        for obj in selection:
            normalize_scale.normalize_scale(float(self.scale_le.text()), obj, axis=self.axis_cmbx.currentText())

        self.close()


def main():
    try:
        cmds.deleteUI("NormalizeScaleUI")
    except Exception:
        pass

    dialog = NormalizeScaleUI()
    dialog.show()


if __name__ == "__main__":
    main()