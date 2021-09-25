import os
import re
import logging

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import pymel.core as pm
import maya.OpenMaya as OpenMaya

from pyqt_commons import MWidgets

from maya_core.pipeline.Asset import asset_utils
from maya_core.pipeline.Asset.publish import publish_stage

STAGES = ['build', 'model', 'lookdev', 'hair', 'rig', 'dress', 'lighting']

logger = logging.getLogger(__name__)
logger.setLevel(10)


class PublishStageUI(QtWidgets.QMainWindow):
    def __init__(self, parent=MWidgets.maya_main_window()):
        super(PublishStageUI, self).__init__(parent)

        self.setWindowTitle("Publish Stage")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.setObjectName("PublishStageUI")

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.asset_node = None
        self.valid_selection = False
        self.valid_version = False

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

        self.validate()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.stage_lble = MWidgets.LabeledLineEdit("Stage: ")
        self.stage_lble.le_widget.setReadOnly(True)

        self.version_lble = MWidgets.LabeledLineEdit("Version: ")

        file_path = cmds.file(q=True, sn=True).replace("\\", "/")
        file_name = file_path.split("/")[-1]

        stage = file_path.split("/")[9].split("_")[-1]

        self.stage_lble.setText(stage)

        version_matches = list(set(re.findall("v\d{3}.ma$", file_name)))

        if version_matches:
            version_number = version_matches[0].replace(".ma", "")
            self.version_lble.setText(version_number)

        self.refresh_btn = QtWidgets.QPushButton()
        icon = QtGui.QIcon(r"F:\share\tools\shelf_icons\reload.png")
        self.refresh_btn.setIcon(icon)

        self.status_le = QtWidgets.QLineEdit()
        self.status_le.setReadOnly(True)

        self.publish_btn = QtWidgets.QPushButton("Publish")

    def create_layout(self):
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)

        stage_layout = QtWidgets.QHBoxLayout()
        stage_layout.addWidget(self.stage_lble)
        stage_layout.addWidget(self.version_lble)

        main_layout.addLayout(stage_layout)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.status_le)
        btn_layout.addWidget(self.publish_btn)

        main_layout.addLayout(btn_layout)

    def create_connections(self):
        self.version_lble.le_widget.textChanged.connect(self.validate)
        self.publish_btn.clicked.connect(self.publish_stage)
        self.refresh_btn.clicked.connect(self.validate)

    def validate(self):
        text = self.version_lble.text()

        # Check for correct format
        self.valid_version = False
        if re.search("^v\d{3}$", text):
            self.valid_version = True

        self.check_world_node()

        # Check to see if version already exists
        if self.valid_selection:
            asset_data_tmp = {
                'asset_name': self.asset_node.assetName.get(),
                'asset_type': self.asset_node.assetType.get()
            }

            asset_data = asset_utils.get_asset_data(asset_data_tmp)

            stage = self.stage_lble.text()

            if stage not in asset_data['stages'].keys() and self.valid_version:
                self.valid_version = True
            elif stage in asset_data['stages'].keys():
                current_version = asset_data['stages'][stage]
                if self.version_lble.text() == current_version:
                    self.valid_version = False

        # Check for valid file name
        self.matches_version = False

        file_name = cmds.file(q=True, sn=True).replace("\\", "/").split("/")[-1]
        version_matches = list(set(re.findall("v\d{3}.ma$", file_name)))

        if version_matches:
            version_number = version_matches[0].replace(".ma", "")

            if version_number == self.version_lble.text():
                self.matches_version = True

        if self.valid_selection and not self.valid_version:
            self.status_le.setText("Invalid verision")
            self.status_le.setStyleSheet("color: red;")
            self.version_lble.le_widget.setStyleSheet("color: red;")
        elif not self.valid_selection and self.valid_version:
            self.status_le.setText("Invalid selection")
            self.status_le.setStyleSheet("color: red;")
            self.version_lble.le_widget.setStyleSheet("")
        elif not self.valid_version and not self.valid_selection:
            self.status_le.setText("Invalid selection and version")
            self.status_le.setStyleSheet("color: red;")
            self.version_lble.le_widget.setStyleSheet("color: red;")
        elif not self.matches_version:
            self.status_le.setText("Version number must match file name")
            self.status_le.setStyleSheet("color: red;")
            self.version_lble.le_widget.setStyleSheet("color: red;")
        elif self.valid_version and self.valid_selection:
            self.status_le.setText("Asset ready for publishing")
            self.status_le.setStyleSheet("")
            self.version_lble.le_widget.setStyleSheet("")

    def check_world_node(self):
        self.valid_selection = False

        if not pm.ls(sl=1) or len(pm.ls(sl=1)) > 1:
            self.valid_selection = False
            return
        elif pm.ls(sl=1) and len(pm.ls(sl=1)) == 1:
            node = pm.ls(sl=1)[0]

            if not hasattr(node, "assetName"):
                self.status_le.setText("Select asset world node")
            else:
                self.status_le.setText("{} selected".format(node.assetName.get()))
                self.asset_node = node
                self.valid_selection = True

    def publish_stage(self):
        self.validate()

        if self.valid_selection and self.valid_version and self.matches_version:
            pass
        else:
            return

        publish_stage.publish_stage(self.asset_node, self.stage_lble.text())

        asset_data_tmp = {
            'asset_name': self.asset_node.assetName.get(),
            'asset_type': self.asset_node.assetType.get()
        }

        asset_data = asset_utils.get_asset_data(asset_data_tmp)

        if asset_data['stages'][self.stage_lble.text()] == self.version_lble.text():
            logger.info("Stage: %s, version: %s for %s published successfully", self.stage_lble.text(),
                        self.version_lble.text(), asset_data['asset_name'])

        self.close()


def main():
    try:
        cmds.deleteUI("PublishStageUI")
    except Exception:
        pass

    file_path = cmds.file(q=True, sn=True).replace("\\", "/")

    search_pattern = "({})".format("|".join(["0{0}_{1}".format(i + 1, s) for i, s in enumerate(STAGES)]))

    if not re.search(search_pattern, file_path):
        logger.error("Cannot launch from a non stage file")
        return

    dialog = PublishStageUI()
    dialog.show()


if __name__ == "__main__":
    main()
