import os
import re
import json
import logging

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import pymel.core as pm

from pyqt_commons import MWidgets
from maya_core.pipeline.project import maya_project
from maya_core.pipeline.Asset import asset_utils
from maya_core.pipeline.Asset.publish import publish_stage

logger = logging.getLogger(__name__)
logger.setLevel(10)


class ExampleDialog(QtWidgets.QMainWindow):
    def __init__(self, parent=MWidgets.maya_main_window()):
        super(ExampleDialog, self).__init__(parent)

        self.setWindowTitle("Publish Asset Stage")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.setObjectName("ExampleDialog")

        self.project = maya_project.get_current_project()

        self.setMinimumWidth(600)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.file_name_lble = MWidgets.LabeledLineEdit("Saving as: ")
        self.file_name_lble.le_widget.setReadOnly(True)

        self.stage_lble = MWidgets.LabeledLineEdit("Stage: ")
        self.stage_lble.le_widget.setReadOnly(True)

        self.version_lbl = QtWidgets.QLabel("Version: ")
        self.current_version_le = QtWidgets.QLineEdit()
        self.current_version_le.setReadOnly(True)
        self.next_version_lbl = QtWidgets.QLabel("->")
        self.next_version_le = QtWidgets.QLineEdit()
        self.next_version_le.setReadOnly(True)

        self.asset_lble = MWidgets.LabeledLineEdit("Asset: ")
        self.asset_lble.le_widget.setReadOnly(True)

        self.stages_tw = QtWidgets.QTreeWidget()
        header_item = QtWidgets.QTreeWidgetItem(["Stage", "Published Version", "Node Version"])
        self.stages_tw.setHeaderItem(header_item)

        self.publish_stage_btn = QtWidgets.QPushButton("Publish Stage")

        self.refresh_btn = QtWidgets.QPushButton()
        icon = QtGui.QIcon(r"F:\share\tools\shelf_icons\reload.png")
        self.refresh_btn.setIcon(icon)

        self.refresh_details()

    def create_layout(self):
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)

        row_1_layout = QtWidgets.QHBoxLayout()
        row_1_layout.addWidget(self.asset_lble)
        row_1_layout.addWidget(self.stage_lble)

        row_2_layout = QtWidgets.QHBoxLayout()
        row_2_layout.addWidget(self.version_lbl)
        row_2_layout.addWidget(self.current_version_le)
        row_2_layout.addWidget(self.next_version_lbl)
        row_2_layout.addWidget(self.next_version_le)

        main_layout.addLayout(row_1_layout)
        main_layout.addLayout(row_2_layout)
        main_layout.addWidget(self.stages_tw)
        main_layout.addWidget(self.file_name_lble)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.publish_stage_btn)

        main_layout.addLayout(btn_layout)
        main_layout.addStretch()

    def create_connections(self):
        self.refresh_btn.clicked.connect(self.refresh_details)
        self.publish_stage_btn.clicked.connect(self.publish_stage)

    def publish_stage(self):
        publish_stage.publish_stage(self.asset, self.stage_lble.text(), version=self.next_version_le.text())

        asset_data_tmp = {
            'asset_name': self.asset.assetName.get(),
            'asset_type': self.asset.assetType.get()
        }

        asset_data = asset_utils.get_asset_data(asset_data_tmp)

        if asset_data['stages'][self.stage_lble.text()] == self.next_version_lbl.text():
            logger.info("Stage: %s, version: %s for %s published successfully", self.stage_lble.text(),
                        self.version_lble.text(), asset_data['asset_name'])

        self.refresh_details()

    def refresh_details(self):
        # File name
        file_path = cmds.file(q=True, sn=True).replace("\\", "/")
        file_name = file_path.split("/")[-1]

        # Asset
        self.asset = [n for n in pm.ls(assemblies=1) if hasattr(n, "mayaAsset")][0]
        self.asset_lble.setText(self.asset.assetName.get())

        asset_data_tmp = {
            'asset_name': self.asset.assetName.get(),
            'asset_type': self.asset.assetType.get()
        }
        asset_data = asset_utils.get_asset_data(asset_data_tmp)

        # Stage
        stage = file_path.split("/")[-3].split("_")[-1]
        self.stage_lble.setText(stage)

        # Version
        current_version_no = list(set(re.findall("v\d{3}", file_name)))[0]
        self.current_version_le.setText(current_version_no)

        next_version_no = "v" + format((int(current_version_no.split("v")[-1]) + 1), '03')

        if current_version_no == "v001":
            if stage not in asset_data['stages'].keys():
                next_version_no = "v001"

        self.next_version_le.setText(next_version_no)

        new_file_name = file_path.replace(current_version_no, next_version_no)
        self.file_name_lble.setText(new_file_name)

        self.refresh_stages_tw()

    def refresh_stages_tw(self):
        self.stages_tw.clear()
        asset_data_tmp = {
            'asset_name': self.asset.assetName.get(),
            'asset_type': self.asset.assetType.get()
        }

        asset_data = asset_utils.get_asset_data(asset_data_tmp)

        for stage, version in asset_data['stages'].items():
            stage_item = QtWidgets.QTreeWidgetItem()
            stage_item.setText(0, stage)
            stage_item.setText(1, version)

            if hasattr(self.asset, "build{}".format(stage.capitalize())):
                stage_item.setText(2, getattr(self.asset, "build{}".format(stage.capitalize())).get())

            self.stages_tw.addTopLevelItem(stage_item)

        pass


def main():
    file_path = cmds.file(q=True, sn=True).replace("\\", "/")
    assets = [n for n in pm.ls(assemblies=1) if hasattr(n, "mayaAsset")]

    if not file_path:
        logger.error("File must be saved first")
        return

    if len(assets) > 1:
        logger.error("More than one top level asset in scene")
        return
    elif not assets:
        logger.error("No assets in scene")
        return

    asset = assets[0]
    asset_name = asset.assetName.get()
    asset_type = asset.assetType.get()

    stages = ['01_build', '02_model', '03_lookdev', '04_hair', '05_rig', '06_dress', '07_lighting', '08_fx']

    check_path = os.path.join(maya_project.get_current_project().assets_path, asset_type, asset_name[0].lower(),
                              asset_name)

    r = ("^" + check_path + "/(" + "|".join(stages) + ")" + "/wip").replace("\\", "/")
    if not re.search(r, file_path):
        logger.error("File not saved in stage wip folder")
        return

    check_file_name = "^{0}_({1})_v\d".format(asset_name, "|".join([s.split("_")[-1] for s in stages])) + "{3}.ma$"

    if not re.search(check_file_name, file_path.split("/")[-1]):
        logger.error("File name is invalid")
        return

    try:
        cmds.deleteUI("ExampleDialog")
    except Exception:
        pass

    dialog = ExampleDialog()
    dialog.show()


if __name__ == "__main__":
    main()
