from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds

from pyqt_commons import MWidgets
from maya_core.material_builder import MaterialBuilderWidget
from maya_core.asset_manager.asset_builder import AssetBuilder

reload(MWidgets)
reload(MaterialBuilderWidget)
reload(AssetBuilder)

from maya_core.common_tools import logger

log = logger.Logger()
log.status = True


class AssetBuilderWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=MWidgets.maya_main_window()):
        super(AssetBuilderWindow, self).__init__(parent)

        self.setWindowTitle("Asset Builder")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setFixedWidth(600)

        self.setObjectName("AssetBuilderWindow")

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        file_browse_icon = QtGui.QIcon(':fileOpen.png')
        icon_size = 40

        # Name
        self.name_lble = MWidgets.LabeledLineEdit("Asset Name ")

        # Preview
        self.preview_lble = MWidgets.LabeledLineEdit("Preview ")
        self.preview_btn = MWidgets.ImagePushButton(icon_size, icon_size)
        self.preview_btn.set_image(file_browse_icon)

        # Tags
        self.tags_lble = MWidgets.LabeledLineEdit("Tags ")

        # Type Cmbx
        self.asset_type_lbl = QtWidgets.QLabel("Asset Type ")
        self.asset_type_cmbx = QtWidgets.QComboBox()
        self.asset_type_cmbx.addItems(["model", "material"])

        # Mesh
        self.mesh_lble = MWidgets.LabeledLineEdit("Mesh ")
        self.mesh_btn = MWidgets.ImagePushButton(icon_size, icon_size)
        self.mesh_btn.set_image(file_browse_icon)

        # Proxy
        self.create_proxy_cb = QtWidgets.QCheckBox("Create Proxy")

        # Scale
        self.scale_lble = MWidgets.LabeledLineEdit("Object Scale ")

        # Material Info
        self.material_widget = MaterialBuilderWidget.MaterialBuilderWidget(icon_size)
        self.material_widget.assign_cb.setHidden(True)
        self.material_widget.debug_cb.setHidden(True)
        self.material_widget.create_empty.setHidden(True)

        # Buttons
        self.build_btn = QtWidgets.QPushButton("Build")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")

    def create_layout(self):
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)
        m = 15
        main_layout.setContentsMargins(m, m, m, m)

        main_layout.addWidget(self.name_lble)
        main_layout.addWidget(MWidgets.QHLine())

        preview_layout = QtWidgets.QHBoxLayout()
        preview_layout.addWidget(self.preview_lble)
        preview_layout.addWidget(self.preview_btn)

        main_layout.addLayout(preview_layout)
        main_layout.addWidget(MWidgets.QHLine())

        asset_type_layout = QtWidgets.QHBoxLayout()
        asset_type_layout.addWidget(self.asset_type_lbl)
        asset_type_layout.addWidget(self.asset_type_cmbx)
        asset_type_layout.addWidget(self.tags_lble)

        main_layout.addLayout(asset_type_layout)
        main_layout.addWidget(MWidgets.QHLine())

        mesh_layout = QtWidgets.QHBoxLayout()
        mesh_layout.addWidget(self.mesh_lble)
        mesh_layout.addWidget(self.mesh_btn)
        mesh_layout.addWidget(self.create_proxy_cb)

        main_layout.addLayout(mesh_layout)
        main_layout.addWidget(MWidgets.QHLine())
        main_layout.addWidget(self.material_widget)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.build_btn)
        btn_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(btn_layout)

        main_layout.addStretch()

    def create_connections(self):
        self.build_btn.clicked.connect(self.build_asset)
        self.mesh_btn.clicked.connect(self.browse_model)
        self.preview_btn.clicked.connect(self.browse_preview)

    def browse_preview(self):
        file_name = QtWidgets.QFileDialog.getOpenFileName(self, 'Select Preview Image')[0]
        if file_name.endswith('png') or file_name.endswith('jpg') or file_name.endswith('jpeg'):
            self.preview_lble.setText(file_name)
        else:
            return

    def browse_model(self):
        old_models_path = r'F:\share\assets_old\models\src'

        file_name = QtWidgets.QFileDialog.getOpenFileName(self, 'Select Mesh', old_models_path)[0]
        if file_name.endswith('obj') or file_name.endswith('fbx'):
            self.mesh_lble.setText(file_name)
        else:
            return

    def build_asset(self):
        # gather asset data to pass to the maya process
        reload(AssetBuilder)

        asset_data = {
            "name": self.name_lble.text(),
            "type": self.asset_type_cmbx.currentText(),
            "tags": self.tags_lble.text(),
            "mesh": self.mesh_lble.text(),
            "preview": self.preview_lble.text(),
            "material": self.material_widget.get_material_data(),
            "scale": self.scale_lble.text(),
        }

        if self.create_proxy_cb.checkState():
            asset_data["has_proxy"] = True
        else:
            asset_data["has_proxy"] = False

        asset_builder = AssetBuilder.AssetBuilder(asset_data)


def main():
    try:
        cmds.deleteUI("AssetBuilderWindow")
    except Exception:
        pass

    dialog = AssetBuilderWindow()
    dialog.show()


if __name__ == "__main__":
    main()
