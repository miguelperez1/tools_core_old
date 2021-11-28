from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds

from pyqt_commons import MWidgets
from maya_core.lookdev.material_utils import material_utils


tex_types = material_utils.TEX_TYPES


class MaterialWidgetFileBrowse(QtWidgets.QWidget):
    def __init__(self, label):
        super(MaterialWidgetFileBrowse, self).__init__()

        self.fb = MWidgets.FileBrowseWidget(label)
        self.cb = QtWidgets.QCheckBox()
        self.ptex_cb = QtWidgets.QCheckBox("Ptex")

        self.fb.fb_btn.clicked.connect(self.set_cb)

        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.addWidget(self.cb)
        self.main_layout.addWidget(self.fb)

        self.main_layout.addWidget(self.ptex_cb)

        self.setContentsMargins(0, 0, 0, 0)

    def set_cb(self):
        if self.fb.lble_widget.le_widget.text():
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
            tex_browse_widget.fb.lble_widget.lbl_widget.setFixedWidth(self.width() * .15)

            self.tex_browse_widgets.append(tex_browse_widget)

        self.create_all_cb = QtWidgets.QCheckBox("Create All")
        self.ptex_all_cb = QtWidgets.QCheckBox("All Ptex")

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        name_type_layout = QtWidgets.QHBoxLayout()
        name_type_layout.setContentsMargins(0, 0, 0, 0)
        name_type_layout.addWidget(self.mat_name_lble)
        name_type_layout.addWidget(self.material_type_cmbx)
        name_type_layout.addWidget(self.create_all_cb)
        name_type_layout.addWidget(self.ptex_all_cb)

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
        self.ptex_all_cb.stateChanged.connect(self.ptex_all_cb_callback)

    def create_all_cb_callback(self):
        for tex in self.tex_browse_widgets:
            tex.cb.setChecked(self.create_all_cb.isChecked())

    def ptex_all_cb_callback(self):
        for tex in self.tex_browse_widgets:
            tex.ptex_cb.setChecked(self.ptex_all_cb.isChecked())

    def get_material_data(self):
        material_data = {
            'name': self.mat_name_lble.text(),
            'material_type': self.material_type_cmbx.currentText(),
            'textures': {}
        }

        textures = []
        for tex in self.tex_browse_widgets:
            if tex.cb.isChecked():
                material_data['textures'][tex.fb.lble_widget.lbl_widget.text().lower()] = {
                    'use_ptex': tex.ptex_cb.isChecked(),
                    'path': tex.fb.lble_widget.le_widget.text()
                }

        return material_data

    def populate_from_asset(self):
        pass


def main():
    try:
        cmds.deleteUI("MaterialBuilderWidget")
    except Exception:
        pass

    dialog = MaterialBuilderWidget(250, 250)
    dialog.show()


if __name__ == "__main__":
    main()
