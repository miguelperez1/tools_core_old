import os
import re
import logging

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import pymel.core as pm

from pyqt_commons import MWidgets
from pyqt_commons import DockableWidget
from maya_core.pipeline.project import maya_project
from maya_core.pipeline.Asset import Asset

projects_root = r"F:\share\projects"

logger = logging.getLogger(__name__)
logger.setLevel(10)


class ProjectToolsUI(DockableWidget.DockableWidget):
    WINDOW_TITLE = "Project Tools"

    def __init__(self):
        self.maya_project = maya_project.get_current_project()

        super(ProjectToolsUI, self).__init__()

        self.setContentsMargins(20, 20, 20, 20)

    def create_actions(self):
        pass

    def create_widgets(self):
        file_browse_icon = QtGui.QIcon(':fileOpen.png')

        self.project_hdrlbl = MWidgets.HeaderLabel("Project Tools", 1.5)

        self.projects_lbl = MWidgets.HeaderLabel("Project: ")
        self.projects_cmbx = QtWidgets.QComboBox()
        self.projects_cmbx.setMinimumWidth(150)

        self.projects_open_dir_btn = QtWidgets.QPushButton()
        self.projects_open_dir_btn.setIcon(file_browse_icon)

        self.projects_open_maya_file_btn = QtWidgets.QPushButton()
        self.projects_open_maya_file_btn.setIcon(QtGui.QIcon(r"F:\share\tools\shelf_icons\maya.png"))

        self.create_project_lble = MWidgets.LabeledLineEdit("Project Name: ")

        self.create_project_btn = QtWidgets.QPushButton("Create")

        self.seq_lbl = QtWidgets.QLabel("Sequence: ")
        self.seq_cmbx = QtWidgets.QComboBox()
        self.seq_create_btn = QtWidgets.QPushButton("Create")

        self.shot_lbl = QtWidgets.QLabel("Shot: ")
        self.shot_cmbx = QtWidgets.QComboBox()
        self.shot_create_btn = QtWidgets.QPushButton("Create")

        self.create_asset_lble = MWidgets.LabeledLineEdit("Create Asset: ")
        self.create_asset_type_cmbx = QtWidgets.QComboBox()
        self.create_valid_asset = False

        self.create_asset_type_cmbx.addItems(['Character', 'Prop', 'Set', 'Transit'])
        self.create_asset_btn = QtWidgets.QPushButton("Create")

        self.asset_browse_lble = MWidgets.LabeledLineEdit("Asset: ")
        assets = maya_project.get_current_project().get_assets()[1]
        self.asset_completer = QtWidgets.QCompleter(assets)
        self.asset_browse_lble.le_widget.setCompleter(self.asset_completer)
        self.valid_asset = False

        self.open_asset_dir_btn = QtWidgets.QPushButton()
        self.open_asset_dir_btn.setIcon(file_browse_icon)

        self.open_asset_maya_btn = QtWidgets.QPushButton()
        self.open_asset_maya_btn.setIcon(QtGui.QIcon(r"F:\share\tools\shelf_icons\open_maya.png"))

        self.import_asset_maya_btn = QtWidgets.QPushButton()
        self.import_asset_maya_btn.setIcon(QtGui.QIcon(r"F:\share\tools\shelf_icons\import_maya.png"))

        self.reference_asset_maya_btn = QtWidgets.QPushButton()
        self.reference_asset_maya_btn.setIcon(QtGui.QIcon(r"F:\share\tools\shelf_icons\reference_maya.png"))

        self.open_shot_btn = QtWidgets.QPushButton()
        self.open_shot_btn.setIcon(file_browse_icon)

        self.refresh_projects()

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        header_layout = QtWidgets.QVBoxLayout()

        header_layout.addWidget(self.project_hdrlbl)
        header_layout.addWidget(MWidgets.QHLine())
        # header_layout.addWidget(MWidgets.VSpacerWidget(25))

        main_layout.addLayout(header_layout)

        inner_layout = QtWidgets.QVBoxLayout()
        inner_layout.setContentsMargins(25, 15, 0, 0)

        set_layout = QtWidgets.QHBoxLayout()
        set_layout.addWidget(self.projects_lbl)
        set_layout.addWidget(self.projects_cmbx)
        set_layout.addWidget(self.projects_open_dir_btn)
        set_layout.addWidget(self.projects_open_maya_file_btn)
        set_layout.addStretch()

        inner_layout.addLayout(set_layout)
        inner_layout.addWidget(MWidgets.QHLine())

        shot_seq_layout = QtWidgets.QHBoxLayout()
        shot_seq_layout.addWidget(self.seq_lbl)
        shot_seq_layout.addWidget(self.seq_cmbx)
        shot_seq_layout.addWidget(self.seq_create_btn)
        shot_seq_layout.addWidget(self.shot_lbl)
        shot_seq_layout.addWidget(self.shot_cmbx)
        shot_seq_layout.addWidget(self.shot_create_btn)
        shot_seq_layout.addWidget(self.open_shot_btn)
        shot_seq_layout.addStretch()

        inner_layout.addLayout(shot_seq_layout)

        browse_asset_layout = QtWidgets.QHBoxLayout()
        browse_asset_layout.addWidget(self.asset_browse_lble)
        browse_asset_layout.addWidget(self.open_asset_dir_btn)
        browse_asset_layout.addWidget(self.open_asset_maya_btn)
        browse_asset_layout.addWidget(self.import_asset_maya_btn)
        browse_asset_layout.addWidget(self.reference_asset_maya_btn)

        create_asset_layout = QtWidgets.QHBoxLayout()
        create_asset_layout.addWidget(self.create_asset_lble)
        create_asset_layout.addWidget(self.create_asset_type_cmbx)
        create_asset_layout.addWidget(self.create_asset_btn)

        inner_layout.addWidget(MWidgets.QHLine())
        inner_layout.addLayout(browse_asset_layout)
        inner_layout.addLayout(create_asset_layout)

        create_layout = QtWidgets.QHBoxLayout()
        create_layout.addWidget(self.create_project_lble)
        create_layout.addWidget(self.create_project_btn)

        main_layout.addLayout(inner_layout)
        main_layout.addStretch()
        main_layout.addLayout(create_layout)

    def create_connections(self):
        self.projects_cmbx.currentTextChanged.connect(self.set_project)
        self.create_project_btn.clicked.connect(self.create_btn_callback)
        self.projects_open_dir_btn.clicked.connect(self.open_project_root)
        self.projects_open_maya_file_btn.clicked.connect(self.open_maya_file)
        self.create_asset_btn.clicked.connect(self.create_asset_btn_callback)
        self.asset_browse_lble.le_widget.textChanged.connect(self.browse_asset_callback)
        self.open_asset_dir_btn.clicked.connect(self.open_asset_dir_btn_callback)
        self.open_asset_maya_btn.clicked.connect(self.open_asset_maya_btn_callback)
        self.import_asset_maya_btn.clicked.connect(self.import_asset_maya_btn_callback)
        self.reference_asset_maya_btn.clicked.connect(self.reference_asset_maya_btn_callback)
        self.create_asset_lble.le_widget.textChanged.connect(self.create_asset_le_callback)

    def create_asset_le_callback(self):
        self.create_valid_asset = True

        if self.create_asset_lble.text() in self.maya_project.get_assets()[-1]:
            self.create_valid_asset = False

        if re.search("(\W|\d|_)", self.create_asset_lble.text()):
            self.create_valid_asset = False

        if not self.create_valid_asset:
            self.create_asset_lble.le_widget.setStyleSheet("color: red;")

        else:
            self.create_asset_lble.le_widget.setStyleSheet("")

    def open_project_root(self):
        os.startfile(self.maya_project.maya_path)

    def open_asset_dir_btn_callback(self):
        if not self.valid_asset:
            return

        asset_name = self.asset_browse_lble.text()
        asset_type = self.maya_project.get_asset(asset_name)[-1]
        asset_root_path = os.path.join(self.maya_project.assets_path, asset_type, asset_name[0].lower(), asset_name)

        if os.path.isdir(asset_root_path):
            os.startfile(asset_root_path)

    def open_asset_maya_btn_callback(self):
        if not self.valid_asset:
            return

        asset_name = self.asset_browse_lble.text()
        asset_type = self.maya_project.get_asset(asset_name)[-1]
        asset_root_path = os.path.join(self.maya_project.assets_path, asset_type, asset_name[0].lower(), asset_name)

        multipleFilters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)"

        if cmds.file(q=True, modified=True):
            result = QtWidgets.QMessageBox.question(self, 'Modified',
                                                    'Current scene has unsaved changes. Continue?')
            if result == QtWidgets.QMessageBox.StandardButton.Yes:
                f = pm.fileDialog2(fileFilter=multipleFilters, fileMode=1, dir=asset_root_path)[0]

                if not os.path.isfile(f):
                    return

                cmds.file(f, open=True, ignoreVersion=True, force=True)
            else:
                return
        else:
            f = pm.fileDialog2(fileFilter=multipleFilters, fileMode=1, dir=asset_root_path)[0]

            if not os.path.isfile(f):
                return

            cmds.file(f, open=True, ignoreVersion=True, force=True)

    def import_asset_maya_btn_callback(self):
        if not self.valid_asset:
            return

        asset_name = self.asset_browse_lble.text()
        asset_type = self.maya_project.get_asset(asset_name)[-1]
        asset_root_path = os.path.join(self.maya_project.assets_path, asset_type, asset_name[0].lower(), asset_name)

        multipleFilters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)"

        f = pm.fileDialog2(fileFilter=multipleFilters, fileMode=1, dir=asset_root_path)[0]

        if not os.path.isfile(f):
            return

        cmds.file(f, i=True, ignoreVersion=True, force=True)

    def reference_asset_maya_btn_callback(self):
        if not self.valid_asset:
            return

        asset_name = self.asset_browse_lble.text()
        asset_type = self.maya_project.get_asset(asset_name)[-1]
        asset_root_path = os.path.join(self.maya_project.assets_path, asset_type, asset_name[0].lower(), asset_name)

        multipleFilters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)"

        f = pm.fileDialog2(fileFilter=multipleFilters, fileMode=1, dir=asset_root_path)[0]

        if not os.path.isfile(f):
            return

        if not f.replace("\\", "/").startswith(asset_root_path.replace("\\", "/")):
            logger.error("Only asset files can be referenced")
            return

        cmds.file(f, r=True, ignoreVersion=True, force=True)

    def browse_asset_callback(self):
        self.valid_asset = False

        for asset_type, assets in self.maya_project.get_assets()[0].items():
            for asset in assets:
                if self.asset_browse_lble.text() == asset:
                    self.valid_asset = True
                    logger.debug("found asset: %s, asset_type: %s", asset, asset_type)
                    break

        if self.valid_asset:
            self.asset_browse_lble.le_widget.setStyleSheet("color: green;")
        else:
            self.asset_browse_lble.le_widget.setStyleSheet("color: red;")

    def open_maya_file(self):
        project_root = os.path.join(projects_root, self.projects_cmbx.currentText(), "scenes")
        multipleFilters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)"

        if cmds.file(q=True, modified=True):
            result = QtWidgets.QMessageBox.question(self, 'Modified',
                                                    'Current scene has unsaved changes. Continue?')
            if result == QtWidgets.QMessageBox.StandardButton.Yes:
                f = pm.fileDialog2(fileFilter=multipleFilters, fileMode=1, dir=project_root)[0]

                cmds.file(f, open=True, ignoreVersion=True, force=True)
            else:
                return

    def create_btn_callback(self):
        self.projects_cmbx.blockSignals(True)
        if self.create_project_lble.text():
            self.maya_project = maya_project.Project(self.create_project_lble.text())
            self.maya_project.create_maya_project()
            self.refresh_projects()
        self.projects_cmbx.blockSignals(False)

    def set_project(self):
        maya_project.set_maya_project(self.projects_cmbx.currentText())
        self.maya_project = maya_project.get_current_project()

        self.asset_completer.setModel(QtCore.QStringListModel(self.maya_project.get_assets()[1], self.asset_completer))

        self.refresh_seq()

    def refresh_projects(self):
        self.projects_cmbx.blockSignals(True)
        self.projects_cmbx.clear()

        for project in os.listdir(projects_root):
            if project == 'archive' or not os.path.isdir(os.path.join(projects_root, project)):
                continue

            self.projects_cmbx.addItem(project)

        current_project = cmds.workspace(sn=1).split("/")[-1]

        if current_project in os.listdir(projects_root):
            self.projects_cmbx.setCurrentText(current_project)
            self.maya_project = maya_project.Project(current_project)

        self.refresh_seq()

        self.projects_cmbx.blockSignals(False)

    def refresh_seq(self):
        self.seq_cmbx.blockSignals(True)
        self.seq_cmbx.clear()

        # replace this with sequences manifest
        for seq in sorted(os.listdir(self.maya_project.seq_path)):
            self.seq_cmbx.addItem(seq)

        self.seq_cmbx.setCurrentIndex(0)

        self.seq_cmbx.blockSignals(False)

        self.refresh_shots()

    def refresh_shots(self):
        self.shot_cmbx.blockSignals(True)
        self.shot_cmbx.clear()

        if self.seq_cmbx.currentText():
            # change this to get from sequence manifest
            for shot in os.listdir(os.path.join(self.maya_project.seq_path, self.seq_cmbx.currentText())):
                self.shot_cmbx.addItem(shot)

        self.shot_cmbx.blockSignals(False)

    def create_asset_btn_callback(self):
        if self.create_valid_asset:
            proj = maya_project.get_current_project()
            asset = Asset.Asset(self.create_asset_lble.text(), self.create_asset_type_cmbx.currentText(), proj)

            asset.create_asset()

            self.asset_browse_lble.setText(self.create_asset_lble.text())
            self.create_asset_le_callback()

            self.asset_completer.setModel(
                QtCore.QStringListModel(self.maya_project.get_assets()[1], self.asset_completer))


def main():
    workspace_contorl_name = ProjectToolsUI.get_workspace_control_name()
    if cmds.workspaceControl(workspace_contorl_name, q=True, exists=True):
        cmds.deleteUI(workspace_contorl_name)

    ProjectToolsUI.module_name_override = "project_tools_ui"
    ui = ProjectToolsUI()


if __name__ == "__main__":
    main()
