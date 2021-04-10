from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import maya.cmds as cmds


def normalize_scale(size, object_b):
    b_bbox = cmds.exactWorldBoundingBox(object_b)

    b_y_size = b_bbox[4] - b_bbox[1]

    ratio = size / b_y_size

    b_scale_x = cmds.getAttr('{}.scaleX'.format(object_b))
    b_scale_y = cmds.getAttr('{}.scaleY'.format(object_b))
    b_scale_z = cmds.getAttr('{}.scaleZ'.format(object_b))

    cmds.setAttr('{}.scaleX'.format(object_b), (b_scale_x * ratio))
    cmds.setAttr('{}.scaleY'.format(object_b), (b_scale_y * ratio))
    cmds.setAttr('{}.scaleZ'.format(object_b), (b_scale_z * ratio))
    cmds.makeIdentity(object_b, apply=True, t=1, r=1, s=1, n=0)


def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class ExampleDialog(QtWidgets.QDialog):
    """
    Dialog used to demonstrates many of the standard dialogs available in Qt
    """

    def __init__(self, parent=maya_main_window()):
        super(ExampleDialog, self).__init__(parent)

        self.setWindowTitle("Normalize Scale")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(300)

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

        self.ok_btn = QtWidgets.QPushButton("Scale")

    def create_layout(self):
        scale_layout = QtWidgets.QHBoxLayout()
        scale_layout.addWidget(self.scale_lbl)
        scale_layout.addWidget(self.scale_le)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(scale_layout)
        main_layout.addLayout(btn_layout)

    def create_connections(self):
        self.ok_btn.clicked.connect(self.normalize_scale)

    def normalize_scale(self):
        selection = cmds.selectedNodes()

        for obj in selection:
            normalize_scale(float(self.scale_le.text()), obj)

        self.close()


if __name__ == "__main__" or __name__ == "maya_core.normalize_scale.normalize_scale":

    try:
        example_dialog.close()  # pylint: disable=E0601
        example_dialog.deleteLater()
    except:
        pass

    example_dialog = ExampleDialog()
    example_dialog.show()
