from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import maya.cmds as cmds

from maya_core.common_tools import logger
from maya_core import material_builder
from pyqt_commons import MWidgets

import os

log = logger.Logger()
log.status = False


class MaterialBuilderWidget(QtWidgets.QWidget):
    def __init__(self, icon_size=45, parent=None):
        super(MaterialBuilderWidget, self).__init__(parent)

        self.setObjectName("MaterialBuilderWidget")

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.valid_asset_name = False
        self.valid_mesh = False
        self.icon_size = icon_size

        self.texture_types = ['']

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        file_browse_icon = QtGui.QIcon(':fileOpen.png')

        # diffuse
        self.diff_mat_lbl = QtWidgets.QLabel('Diffuse             ')
        self.diff_mat_le = QtWidgets.QLineEdit()
        self.diff_mat_fb = MWidgets.ImagePushButton(self.icon_size, self.icon_size)
        self.diff_mat_fb.set_image(file_browse_icon)

        # specular
        self.spec_mat_lbl = QtWidgets.QLabel('Specular           ')
        self.spec_mat_le = QtWidgets.QLineEdit()
        self.spec_mat_fb = MWidgets.ImagePushButton(self.icon_size, self.icon_size)
        self.spec_mat_fb.set_image(file_browse_icon)

        # rough
        self.rough_mat_lbl = QtWidgets.QLabel('Rough/Gloss   ')
        self.rough_mat_le = QtWidgets.QLineEdit()
        self.rough_mat_fb = MWidgets.ImagePushButton(self.icon_size, self.icon_size)
        self.rough_mat_fb.set_image(file_browse_icon)

        # normal
        self.normal_mat_lbl = QtWidgets.QLabel('Normal             ')
        self.normal_mat_le = QtWidgets.QLineEdit()
        self.normal_mat_fb = MWidgets.ImagePushButton(self.icon_size, self.icon_size)
        self.normal_mat_fb.set_image(file_browse_icon)

        # opacity
        self.opacity_mat_lbl = QtWidgets.QLabel('Opacity            ')
        self.opacity_mat_le = QtWidgets.QLineEdit()
        self.opacity_mat_fb = MWidgets.ImagePushButton(self.icon_size, self.icon_size)
        self.opacity_mat_fb.set_image(file_browse_icon)

        # displace
        self.disp_mat_lbl = QtWidgets.QLabel('Displacement  ')
        self.disp_mat_le = QtWidgets.QLineEdit()
        self.disp_mat_fb = MWidgets.ImagePushButton(self.icon_size, self.icon_size)
        self.disp_mat_fb.set_image(file_browse_icon)

        # metal
        self.metal_mat_lbl = QtWidgets.QLabel('Metallic            ')
        self.metal_mat_le = QtWidgets.QLineEdit()
        self.metal_mat_fb = MWidgets.ImagePushButton(self.icon_size, self.icon_size)
        self.metal_mat_fb.set_image(file_browse_icon)

        # Build button
        self.build_btn = QtWidgets.QPushButton('Build')
        self.cancel_btn = QtWidgets.QPushButton('Cancel')

        # Material Drop Down
        self.mat_dd_lbl = QtWidgets.QLabel('Material Type: ')
        self.mat_drop_down = QtWidgets.QComboBox()
        self.mat_drop_down.addItems(['VRayMtl', 'VRayMtl2Sided'])

        # asset name
        self.asset_name_lbl = QtWidgets.QLabel('Material Name: ')
        self.asset_name_le = QtWidgets.QLineEdit()

        self.texture_line_edits = [
            self.diff_mat_le,
            self.spec_mat_le,
            self.rough_mat_le,
            self.metal_mat_le,
            self.normal_mat_le,
            self.opacity_mat_le,
            self.disp_mat_le
        ]

        # Rough / Gloss CB
        self.rough_gloss_cb = QtWidgets.QCheckBox("Use Roughness")

        # Assign to Selected
        self.assign_cb = QtWidgets.QCheckBox("Assign to Selection")

        self.debug_cb = QtWidgets.QCheckBox("Debug Mode")

        self.create_empty = QtWidgets.QCheckBox("Create blank nodes")

    def create_layout(self):
        # asset name
        asset_name_layout = QtWidgets.QHBoxLayout()
        asset_name_layout.addWidget(self.asset_name_lbl)
        asset_name_layout.addWidget(self.asset_name_le)

        # diffuse row
        diff_material_row_layout = QtWidgets.QHBoxLayout()
        diff_material_row_layout.addWidget(self.diff_mat_lbl)
        diff_material_row_layout.addWidget(self.diff_mat_le)
        diff_material_row_layout.addWidget(self.diff_mat_fb)

        # spec row
        spec_material_row_layout = QtWidgets.QHBoxLayout()
        spec_material_row_layout.addWidget(self.spec_mat_lbl)
        spec_material_row_layout.addWidget(self.spec_mat_le)
        spec_material_row_layout.addWidget(self.spec_mat_fb)

        # rough row
        rough_material_row_layout = QtWidgets.QHBoxLayout()
        rough_material_row_layout.addWidget(self.rough_mat_lbl)
        rough_material_row_layout.addWidget(self.rough_mat_le)
        rough_material_row_layout.addWidget(self.rough_mat_fb)

        # normal row
        normal_material_row_layout = QtWidgets.QHBoxLayout()
        normal_material_row_layout.addWidget(self.normal_mat_lbl)
        normal_material_row_layout.addWidget(self.normal_mat_le)
        normal_material_row_layout.addWidget(self.normal_mat_fb)

        # displacement row
        disp_material_row_layout = QtWidgets.QHBoxLayout()
        disp_material_row_layout.addWidget(self.disp_mat_lbl)
        disp_material_row_layout.addWidget(self.disp_mat_le)
        disp_material_row_layout.addWidget(self.disp_mat_fb)

        # metallic row
        metal_material_row_layout = QtWidgets.QHBoxLayout()
        metal_material_row_layout.addWidget(self.metal_mat_lbl)
        metal_material_row_layout.addWidget(self.metal_mat_le)
        metal_material_row_layout.addWidget(self.metal_mat_fb)

        # opacity row
        opacity_material_row_layout = QtWidgets.QHBoxLayout()
        opacity_material_row_layout.addWidget(self.opacity_mat_lbl)
        opacity_material_row_layout.addWidget(self.opacity_mat_le)
        opacity_material_row_layout.addWidget(self.opacity_mat_fb)

        # Settings row
        settings_layout = QtWidgets.QHBoxLayout()
        settings_layout.addWidget(self.rough_gloss_cb)
        settings_layout.addWidget(self.assign_cb)
        settings_layout.addWidget(self.debug_cb)
        settings_layout.addStretch()

        # Mat selection layout
        mat_selection_layout = QtWidgets.QHBoxLayout()
        mat_selection_layout.addWidget(self.mat_dd_lbl)
        mat_selection_layout.addWidget(self.mat_drop_down)
        mat_selection_layout.addWidget(self.create_empty)
        mat_selection_layout.addStretch()

        # Main Layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(asset_name_layout)
        main_layout.addWidget(MWidgets.QHLine())
        main_layout.addLayout(mat_selection_layout)
        main_layout.addLayout(diff_material_row_layout)
        main_layout.addLayout(spec_material_row_layout)
        main_layout.addLayout(rough_material_row_layout)
        main_layout.addLayout(metal_material_row_layout)
        main_layout.addLayout(normal_material_row_layout)
        main_layout.addLayout(opacity_material_row_layout)
        main_layout.addLayout(settings_layout)

    def create_connections(self):
        # texture browsers
        self.diff_mat_fb.clicked.connect(self.browse_diffuse)
        self.spec_mat_fb.clicked.connect(self.browse_specular)
        self.rough_mat_fb.clicked.connect(self.browse_roughness)
        self.metal_mat_fb.clicked.connect(self.browse_metallic)
        self.normal_mat_fb.clicked.connect(self.browse_normal)
        self.disp_mat_fb.clicked.connect(self.browse_displace)
        self.opacity_mat_fb.clicked.connect(self.browse_opacity)

    def reset_texture_line_edits(self):
        for widget in self.texture_line_edits:
            widget.setText("")
            widget.setPlaceholderText("")
            widget.setReadOnly(False)
            widget.setStyleSheet("")

    def browse_diffuse(self):
        if self.mat_drop_down.currentText() == 'None':
            QtWidgets.QMessageBox.warning(self, "Warning", "Texture selection not available for 'None' material type.")
            return

        file_name = QtWidgets.QFileDialog.getOpenFileName()[0]
        self.diff_mat_le.setText(file_name)

    def browse_specular(self):
        if self.mat_drop_down.currentText() == 'None':
            QtWidgets.QMessageBox.warning(self, "Warning", "Texture selection not available for 'None' material type.")
            return

        file_name = QtWidgets.QFileDialog.getOpenFileName()[0]
        self.spec_mat_le.setText(file_name)

    def browse_roughness(self):
        if self.mat_drop_down.currentText() == 'None':
            QtWidgets.QMessageBox.warning(self, "Warning", "Texture selection not available for 'None' material type.")
            return

        file_name = QtWidgets.QFileDialog.getOpenFileName()[0]
        self.rough_mat_le.setText(file_name)

    def browse_opacity(self):
        if self.mat_drop_down.currentText() == 'None':
            QtWidgets.QMessageBox.warning(self, "Warning", "Texture selection not available for 'None' material type.")
            return

        file_name = QtWidgets.QFileDialog.getOpenFileName()[0]
        self.opacity_mat_le.setText(file_name)

    def browse_metallic(self):
        if self.mat_drop_down.currentText() == 'None':
            QtWidgets.QMessageBox.warning(self, "Warning", "Texture selection not available for 'None' material type.")
            return

        if self.mat_drop_down.currentText() != 'PxrSurface':
            file_name = QtWidgets.QFileDialog.getOpenFileName()[0]
            self.metal_mat_le.setText(file_name)
        else:
            QtWidgets.QMessageBox.warning(self, "Warning",
                                          "Metallic Texture selection not available for 'PxrSurface' material type.")
            return

    def browse_normal(self):
        if self.mat_drop_down.currentText() == 'None':
            QtWidgets.QMessageBox.warning(self, "Warning", "Texture selection not available for 'None' material type.")
            return

        file_name = QtWidgets.QFileDialog.getOpenFileName()[0]
        self.normal_mat_le.setText(file_name)

    def browse_displace(self):
        if self.mat_drop_down.currentText() == 'None':
            QtWidgets.QMessageBox.warning(self, "Warning", "Texture selection not available for 'None' material type.")
            return

        file_name = QtWidgets.QFileDialog.getOpenFileName()[0]
        self.disp_mat_le.setText(file_name)

    def get_material_data(self):
        asset_data = {
            "name": self.asset_name_le.text(),
            "mat_type": self.mat_drop_down.currentText(),
            "diffuse_tex": self.diff_mat_le.text(),
            "specular_tex": self.spec_mat_le.text(),
            "gloss_tex": self.rough_mat_le.text(),
            "normal_tex": self.normal_mat_le.text(),
            "metallic_tex": self.metal_mat_le.text(),
            "opacity_tex": self.opacity_mat_le.text(),
            "displacement_tex": self.disp_mat_le.text(),
            "use_rough": self.rough_gloss_cb.isChecked(),
            "assign": self.assign_cb.isChecked(),
            "create_empty": self.create_empty.isChecked()
        }

        return asset_data

    def build_material(self):
        selected = cmds.ls(sl=True)

        asset_data = self.get_material_data()

        vray_mtl = material_builder.build_vraymtl(asset_data, self.debug_cb.isChecked())

        if self.mat_drop_down.currentText() == "VRayMtl2Sided":
            vray_2sidedmtl = material_builder.build_vray2sidedmtl(self.asset_name_le.text(), vray_mtl[0], vray_mtl[0])

        if self.assign_cb.isChecked():
            if self.mat_drop_down.currentText() == "VRayMtl2Sided":
                cmds.sets(selected, e=True, forceElement=vray_2sidedmtl[-1])
            else:
                cmds.sets(selected, e=True, forceElement=vray_mtl[-1])
