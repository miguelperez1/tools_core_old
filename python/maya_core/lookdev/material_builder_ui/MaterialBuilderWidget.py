from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds

from pyqt_commons import MWidgets
from maya_core.lookdev.material_utils import material_utils

reload(MWidgets)
reload(material_utils)

tex_types = material_utils.TEX_TYPES


class MaterialWidgetFileBrowse(MWidgets.FileBrowseWidget):
    def __init__(self, label):
        super(MaterialWidgetFileBrowse, self).__init__(label)

        self.cb = QtWidgets.QCheckBox()

        self.fb_btn.clicked.connect(self.set_cb)

        # self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.insertWidget(0, self.cb)

    def set_cb(self):
        if self.lble_widget.le_widget.text():
            self.cb.setChecked(1)


class MaterialBuilderWidget(QtWidgets.QWidget):
    def __init__(self, width, height):
        super(MaterialBuilderWidget, self).__init__()
        self.setObjectName("MaterialBuilderWidget")
        self.size = (width, height)

        self.setMinimumSize(width, height)

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.mat_name_lble = MWidgets.LabeledLineEdit("Material Name")

        self.material_type_cmbx = QtWidgets.QComboBox()

        material_types = ['VRayMtl', 'VRayMtl2Sided']
        self.material_type_cmbx.addItems(material_types)

        self.tex_browse_widgets = []

        for tex_type in tex_types:
            tex_browse_widget = MaterialWidgetFileBrowse(tex_type.capitalize())
            tex_browse_widget.lble_widget.lbl_widget.setFixedWidth(self.width() * .15)

            self.tex_browse_widgets.append(tex_browse_widget)

        self.create_all_cb = QtWidgets.QCheckBox("Create All")

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        name_type_layout = QtWidgets.QHBoxLayout()
        name_type_layout.setContentsMargins(0, 0, 0, 0)
        name_type_layout.addWidget(self.mat_name_lble)
        name_type_layout.addWidget(self.material_type_cmbx)
        name_type_layout.addWidget(self.create_all_cb)

        main_layout.addWidget(MWidgets.QHLine())
        main_layout.addLayout(name_type_layout)
        main_layout.addWidget(MWidgets.QHLine())

        tex_browse_layout = QtWidgets.QVBoxLayout()
        tex_browse_layout.setContentsMargins(0, 0, 0, 0)

        for tex_browse_widget in self.tex_browse_widgets:
            tex_browse_layout.addWidget(tex_browse_widget)

        main_layout.addLayout(tex_browse_layout)

    def create_connections(self):
        self.create_all_cb.stateChanged.connect(self.create_all_cb_callback)

    def create_all_cb_callback(self):
        for tex in self.tex_browse_widgets:
            tex.cb.setChecked(self.create_all_cb.isChecked())

    def get_material_data(self):
        material_data = {
            'name': self.mat_name_lble.text(),
            'material_type': self.material_type_cmbx.currentText()
        }

        textures = []
        for tex in self.tex_browse_widgets:
            if tex.cb.isChecked():
                tex_data = {
                    tex.lble_widget.lbl_widget.text().lower(): tex.lble_widget.le_widget.text()
                }
                textures.append(tex_data)

        material_data['textures'] = textures

        print material_data

        return material_data


def main():
    try:
        cmds.deleteUI("MaterialBuilderWidget")
    except Exception:
        pass

    dialog = MaterialBuilderWidget(250, 250)
    dialog.show()


if __name__ == "__main__":
    main()
