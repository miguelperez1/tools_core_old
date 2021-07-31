from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds

from pyqt_commons import MWidgets

from maya_core.asset_manager.library_utils import library_utils
from maya_core.asset_manager.library_utils import constants
from maya_core.asset_manager.asset_builder import asset_builder

reload(asset_builder)

library_data = {}

for library in constants.libraries.keys():
    library_data[library] = library_utils.get_library_data(library)


class FilePublisherUI(QtWidgets.QMainWindow):
    def __init__(self, parent=MWidgets.maya_main_window()):
        super(FilePublisherUI, self).__init__(parent)

        self.setWindowTitle("Window")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(800)

        self.setObjectName("FilePublisherUI")

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.asset_name_lble = MWidgets.LabeledLineEdit("Asset Name:")

        self.asset_type_cmbx = QtWidgets.QComboBox()
        libraries = constants.libraries.keys()
        libraries.remove("root")
        self.asset_type_cmbx.addItems([library.title() for library in libraries])

        self.tags_lble = MWidgets.LabeledLineEdit("Tags:")

        self.preview_lblebtn = MWidgets.FileBrowseWidget("Preview:")

        self.publish_textures_cb = QtWidgets.QCheckBox("Publish Textures")
        self.create_vrayproxy_cb = QtWidgets.QCheckBox("Create VRay Proxy")
        self.selection_cb = QtWidgets.QCheckBox("Publish Selection")

        self.publish_asset_btn = QtWidgets.QPushButton("Publish Asset File")

    def create_layout(self):
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)

        asset_input_layout = QtWidgets.QHBoxLayout()

        asset_input_layout.addWidget(self.asset_name_lble)
        asset_input_layout.addWidget(self.asset_type_cmbx)

        main_layout.addLayout(asset_input_layout)

        main_layout.addWidget(self.tags_lble)
        main_layout.addWidget(self.preview_lblebtn)

        button_layout = QtWidgets.QHBoxLayout()

        button_layout.addWidget(self.selection_cb)
        button_layout.addWidget(self.publish_textures_cb)
        button_layout.addWidget(self.create_vrayproxy_cb)

        button_layout.addStretch()
        button_layout.addWidget(self.publish_asset_btn)

        main_layout.addLayout(button_layout)

    def create_connections(self):
        self.publish_asset_btn.clicked.connect(self.publish_file)
        self.asset_name_lble.le_widget.textChanged.connect(self.validate_asset_name)

    def publish_file(self):
        # Example asset data structure
        # asset_data = {
        #     'name': '',
        #     'asset_type': 'model',
        #     'preview': None,
        #     'tags': 'megascans',
        #     'mesh': None,
        #     'material_data': None,
        #     'scale': 1,
        #     'has_proxy': 1
        # }

        asset_data = {
            'name': self.asset_name_lble.text().replace(" ", "_"),
            'asset_type': self.asset_type_cmbx.currentText().lower(),
            'preview': self.preview_lblebtn.text(),
            'tags': self.tags_lble.text(),
            'mesh': None,
            'material_data': None,
            'scale': None,
            'has_proxy': self.create_vrayproxy_cb.isChecked()
        }

        builder = asset_builder.AssetBuilder(asset_data)

        if self.valid_asset_name():
            save_type = "selection" if self.selection_cb.isChecked() else "file"

            builder.create_asset(save_type=save_type)

        if self.publish_textures_cb.isChecked():
            if self.selection_cb.isChecked():
                # get materials from selection
                pass
            # publish textures
            # builder.publish_textures()
            pass

    def valid_asset_name(self):
        self.asset_name_lble.le_widget.setStyleSheet("")
        if self.asset_name_lble.text().strip() in library_data[self.asset_type_cmbx.currentText().lower()]['assets']:
            self.asset_name_lble.le_widget.setStyleSheet("color:red;")
            return False
        return True


def main():
    try:
        cmds.deleteUI("FilePublisherUI")
    except Exception:
        pass

    dialog = FilePublisherUI()
    dialog.show()


if __name__ == "__main__":
    main()
