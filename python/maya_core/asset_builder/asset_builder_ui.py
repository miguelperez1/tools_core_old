from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import maya.cmds as cmds

import os
import re
import sys
import subprocess

from maya_core.asset_builder import asset


# TO DO
# ACES Convert

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class QHLine(QtWidgets.QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)


class BuilderWindow(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(BuilderWindow, self).__init__(parent)

        self.setWindowTitle("Asset Builder")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.valid_asset_name = False
        self.valid_mesh = False

        self.setMinimumWidth(500)
        self.setMinimumHeight(400)

        self.texture_types = ['']

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        file_browse_icon = QtGui.QIcon(':fileOpen.png')
        # mesh
        self.mesh_lbl = QtWidgets.QLabel('Mesh: ')
        self.mesh_le = QtWidgets.QLineEdit()
        self.mesh_fb = QtWidgets.QPushButton()
        self.mesh_fb.setIcon(file_browse_icon)

        # scale
        self.scale_lbl = QtWidgets.QLabel('Set Relative Height Scale (ft): ')
        self.scale_le = QtWidgets.QLineEdit()

        # preview
        self.preview_lbl = QtWidgets.QLabel('Preview: ')
        self.preview_le = QtWidgets.QLineEdit()
        self.preview_fb = QtWidgets.QPushButton()
        self.preview_fb.setIcon(file_browse_icon)

        # diffuse
        self.diff_mat_cb = QtWidgets.QLabel('Diffuse             ')
        self.diff_mat_le = QtWidgets.QLineEdit()
        self.diff_mat_fb = QtWidgets.QPushButton()
        self.diff_mat_fb.setIcon(file_browse_icon)

        # specular
        self.spec_mat_cb = QtWidgets.QLabel('Specular           ')
        self.spec_mat_le = QtWidgets.QLineEdit()
        self.spec_mat_fb = QtWidgets.QPushButton()
        self.spec_mat_fb.setIcon(file_browse_icon)

        # rough
        self.rough_mat_cb = QtWidgets.QLabel('Rough/Gloss   ')
        self.rough_mat_le = QtWidgets.QLineEdit()
        self.rough_mat_fb = QtWidgets.QPushButton()
        self.rough_mat_fb.setIcon(file_browse_icon)

        # normal
        self.normal_mat_cb = QtWidgets.QLabel('Normal             ')
        self.normal_mat_le = QtWidgets.QLineEdit()
        self.normal_mat_fb = QtWidgets.QPushButton()
        self.normal_mat_fb.setIcon(file_browse_icon)

        # opacity
        self.opacity_mat_cb = QtWidgets.QLabel('Opacity            ')
        self.opacity_mat_le = QtWidgets.QLineEdit()
        self.opacity_mat_fb = QtWidgets.QPushButton()
        self.opacity_mat_fb.setIcon(file_browse_icon)

        # displace
        self.disp_mat_cb = QtWidgets.QLabel('Displacement  ')
        self.disp_mat_le = QtWidgets.QLineEdit()
        self.disp_mat_fb = QtWidgets.QPushButton()
        self.disp_mat_fb.setIcon(file_browse_icon)

        # metal
        self.metal_mat_cb = QtWidgets.QLabel('Metallic            ')
        self.metal_mat_le = QtWidgets.QLineEdit()
        self.metal_mat_fb = QtWidgets.QPushButton()
        self.metal_mat_fb.setIcon(file_browse_icon)

        # Build button
        self.build_btn = QtWidgets.QPushButton('Build')
        self.cancel_btn = QtWidgets.QPushButton('Cancel')

        # Asset Type Drop Down
        self.asset_type_lbl = QtWidgets.QLabel('Asset Type: ')
        self.asset_type_dd = QtWidgets.QComboBox()
        self.asset_type_dd.addItems(['Model', 'Material'])

        # Asset Library Drop Down
        self.asset_lib_lbl = QtWidgets.QLabel('Asset Library: ')
        self.asset_lib_dd = QtWidgets.QComboBox()
        projects = os.listdir(r'F:\share\projects')
        self.asset_lib_dd.addItems(['General'])
        for project in projects:
            self.asset_lib_dd.addItem(project.capitalize())

        # Material Drop Down
        self.mat_dd_lbl = QtWidgets.QLabel('Material Type: ')
        self.mat_drop_down = QtWidgets.QComboBox()
        self.mat_drop_down.addItems(['VRayMtl', 'None'])

        # asset name
        self.asset_name_lbl = QtWidgets.QLabel('Asset Name: ')
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

    def create_layout(self):
        # asset name
        asset_name_layout = QtWidgets.QHBoxLayout()
        asset_name_layout.addWidget(self.asset_name_lbl)
        asset_name_layout.addWidget(self.asset_name_le)

        # mesh row
        mesh_row_layout = QtWidgets.QHBoxLayout()
        mesh_row_layout.addWidget(self.mesh_lbl)
        mesh_row_layout.addWidget(self.mesh_le)
        mesh_row_layout.addWidget(self.mesh_fb)

        # scale row
        scale_row_layout = QtWidgets.QHBoxLayout()
        scale_row_layout.addWidget(self.scale_lbl)
        scale_row_layout.addWidget(self.scale_le)

        # preview row
        preview_row_layout = QtWidgets.QHBoxLayout()
        preview_row_layout.addWidget(self.preview_lbl)
        preview_row_layout.addWidget(self.preview_le)
        preview_row_layout.addWidget(self.preview_fb)

        # diffuse row
        diff_material_row_layout = QtWidgets.QHBoxLayout()
        diff_material_row_layout.addWidget(self.diff_mat_cb)
        diff_material_row_layout.addWidget(self.diff_mat_le)
        diff_material_row_layout.addWidget(self.diff_mat_fb)

        # spec row
        spec_material_row_layout = QtWidgets.QHBoxLayout()
        spec_material_row_layout.addWidget(self.spec_mat_cb)
        spec_material_row_layout.addWidget(self.spec_mat_le)
        spec_material_row_layout.addWidget(self.spec_mat_fb)

        # rough row
        rough_material_row_layout = QtWidgets.QHBoxLayout()
        rough_material_row_layout.addWidget(self.rough_mat_cb)
        rough_material_row_layout.addWidget(self.rough_mat_le)
        rough_material_row_layout.addWidget(self.rough_mat_fb)

        # normal row
        normal_material_row_layout = QtWidgets.QHBoxLayout()
        normal_material_row_layout.addWidget(self.normal_mat_cb)
        normal_material_row_layout.addWidget(self.normal_mat_le)
        normal_material_row_layout.addWidget(self.normal_mat_fb)

        # displacement row
        disp_material_row_layout = QtWidgets.QHBoxLayout()
        disp_material_row_layout.addWidget(self.disp_mat_cb)
        disp_material_row_layout.addWidget(self.disp_mat_le)
        disp_material_row_layout.addWidget(self.disp_mat_fb)

        # metallic row
        metal_material_row_layout = QtWidgets.QHBoxLayout()
        metal_material_row_layout.addWidget(self.metal_mat_cb)
        metal_material_row_layout.addWidget(self.metal_mat_le)
        metal_material_row_layout.addWidget(self.metal_mat_fb)

        # opacity row
        opacity_material_row_layout = QtWidgets.QHBoxLayout()
        opacity_material_row_layout.addWidget(self.opacity_mat_cb)
        opacity_material_row_layout.addWidget(self.opacity_mat_le)
        opacity_material_row_layout.addWidget(self.opacity_mat_fb)

        # button layout
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.build_btn)
        button_layout.addWidget(self.cancel_btn)

        # Asset Type and Library Layout
        asset_layout = QtWidgets.QHBoxLayout()
        asset_layout.addWidget(self.asset_type_lbl)
        asset_layout.addWidget(self.asset_type_dd)
        asset_layout.addWidget(self.asset_lib_lbl)
        asset_layout.addWidget(self.asset_lib_dd)
        asset_layout.addStretch()

        # Mat selection layout
        mat_selection_layout = QtWidgets.QHBoxLayout()
        mat_selection_layout.addWidget(self.mat_dd_lbl)
        mat_selection_layout.addWidget(self.mat_drop_down)
        mat_selection_layout.addStretch()

        # Main Layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(asset_name_layout)
        main_layout.addLayout(asset_layout)
        main_layout.addWidget(QHLine())
        main_layout.addLayout(preview_row_layout)
        main_layout.addWidget(QHLine())
        main_layout.addLayout(mesh_row_layout)
        main_layout.addLayout(scale_row_layout)
        main_layout.addWidget(QHLine())
        main_layout.addLayout(mat_selection_layout)
        main_layout.addLayout(diff_material_row_layout)
        main_layout.addLayout(spec_material_row_layout)
        main_layout.addLayout(rough_material_row_layout)
        main_layout.addLayout(metal_material_row_layout)
        main_layout.addLayout(normal_material_row_layout)
        main_layout.addLayout(opacity_material_row_layout)
        main_layout.addLayout(disp_material_row_layout)
        main_layout.addLayout(button_layout)

    def create_connections(self):
        # Validate asset name
        self.asset_name_le.textChanged.connect(self.validate_asset_name)

        # Asset Type
        self.asset_type_dd.currentTextChanged.connect(self.asset_type_callback)

        # Cancel
        self.cancel_btn.clicked.connect(self.close)

        # Mesh
        self.mesh_fb.clicked.connect(self.browse_model)

        # Preview
        self.preview_fb.clicked.connect(self.browse_preview)

        # Material type callback
        self.mat_drop_down.currentTextChanged.connect(self.material_dd_callback)

        # texture browsers
        self.diff_mat_fb.clicked.connect(self.browse_diffuse)
        self.spec_mat_fb.clicked.connect(self.browse_specular)
        self.rough_mat_fb.clicked.connect(self.browse_roughness)
        self.metal_mat_fb.clicked.connect(self.browse_metallic)
        self.normal_mat_fb.clicked.connect(self.browse_normal)
        self.disp_mat_fb.clicked.connect(self.browse_displace)
        self.opacity_mat_fb.clicked.connect(self.browse_opacity)

        # Build
        self.build_btn.clicked.connect(self.build_asset)

        pass

    def asset_type_callback(self):
        if self.asset_type_dd.currentText() == 'Material':
            self.mesh_le.setPlaceholderText("Mesh not available for 'Material' asset type.")
            self.mesh_le.setReadOnly(True)
            self.mesh_le.setStyleSheet("color: dark gray;")
            self.scale_le.setPlaceholderText("Mesh not available for 'Material' asset type.")
            self.scale_le.setReadOnly(True)
            self.scale_le.setStyleSheet("color: dark gray;")
        else:
            self.mesh_le.setReadOnly(False)
            self.mesh_le.setPlaceholderText('')
            self.mesh_le.setStyleSheet("")
            self.scale_le.setReadOnly(False)
            self.scale_le.setPlaceholderText('')
            self.scale_le.setStyleSheet("")
        self.validate_asset_name()

    def reset_texture_line_edits(self):
        for widget in self.texture_line_edits:
            widget.setText("")
            widget.setPlaceholderText("")
            widget.setReadOnly(False)
            widget.setStyleSheet("")

    def material_dd_callback(self):
        if self.mat_drop_down.currentText() != 'None':
            if self.mat_drop_down.currentText() == 'PxrSurface':
                self.reset_texture_line_edits()
                self.metal_mat_le.setText("")
                self.metal_mat_le.setPlaceholderText("Metallic texture not available for 'PxrSurface' material type.")
                self.metal_mat_le.setReadOnly(True)
                self.metal_mat_le.setStyleSheet("color: dark gray;")
            else:
                self.reset_texture_line_edits()

        elif self.mat_drop_down.currentText() == 'None':
            for widget in self.texture_line_edits:
                widget.setText("")
                widget.setPlaceholderText("Textures not available for 'None' material type")
                widget.setReadOnly(True)
                widget.setStyleSheet("color: dark gray;")

    def browse_model(self):
        old_models_path = r'F:\share\assets_old\models\src'
        if self.asset_type_dd.currentText() == "Model":
            file_name = QtWidgets.QFileDialog.getOpenFileName(self, 'Select Mesh', old_models_path)[0]
            if file_name.endswith('obj') or file_name.endswith('fbx'):
                self.mesh_le.setText(file_name)
                self.valid_mesh = True
            else:
                return
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "Mesh selection not available for 'Material' asset type.")

    def browse_preview(self):
        thumbnail_path = r'F:\share\assets\libraries\{0}\thumbnails'.format(self.asset_type_dd.currentText())
        file_name = QtWidgets.QFileDialog.getOpenFileName(self, 'Select Preview Image', thumbnail_path)[0]
        if file_name.endswith('png') or file_name.endswith('jpg') or file_name.endswith('jpeg'):
            self.preview_le.setText(file_name)
        else:
            return

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

    def write_temp_data(self):
        tmp_asset_yml_path = r'F:\share\tools\core\maya_core\asset_builder\tmp\{}.yml'.format(self.asset_name_le.text())
        tmp_asset_yml = open(tmp_asset_yml_path, "a")
        tmp_asset_yml.write("{}_asset: \n".format(self.asset_name_le.text()))
        tmp_asset_yml.write("    name: {}\n".format(self.asset_name_le.text()))
        tmp_asset_yml.write("    type: {}\n".format(self.asset_type_dd.currentText().lower()))
        tmp_asset_yml.write("    library: {}\n".format(self.asset_lib_dd.currentText().lower()))
        tmp_asset_yml.write("    preview: {}\n".format(self.preview_le.text()))
        tmp_asset_yml.write("    model: {}\n".format(self.mesh_le.text()))
        tmp_asset_yml.write("    scale: {}\n".format(self.scale_le.text()))
        tmp_asset_yml.write("    material_type: {}\n".format(self.mat_drop_down.currentText()))

        # Convert Diffuse to ACES
        tmp_asset_yml.write("    diffuse_tex: {}\n".format(self.diff_mat_le.text()))
        if self.diff_mat_le.text() != "":
            diff_aces_reply = QtWidgets.QMessageBox.question(self, 'Convert Texture', 'Convert Diffuse to ACES?')
            if diff_aces_reply == QtWidgets.QMessageBox.Yes:
                tmp_asset_yml.write("    diffuse_aces_convert: True\n")
        else:
            tmp_asset_yml.write("    diffuse_aces_convert: False\n")

        # Convert Spec to ACES
        tmp_asset_yml.write("    specular_tex: {}\n".format(self.spec_mat_le.text()))
        if self.spec_mat_le.text() != "":
            spec_aces_reply = QtWidgets.QMessageBox.question(self, 'Convert Texture', 'Convert Specular to ACES?')
            if spec_aces_reply == QtWidgets.QMessageBox.Yes:
                tmp_asset_yml.write("    specular_aces_convert: True\n")
        else:
            tmp_asset_yml.write("    specular_aces_convert: False\n")

        # Invert Roughness
        tmp_asset_yml.write("    roughness_tex: {}\n".format(self.rough_mat_le.text()))
        if self.rough_mat_le.text() != "":
            rough_inv_reply = QtWidgets.QMessageBox.question(self, 'Invert Texture', 'Change Roughness to Gloss?')
            if rough_inv_reply == QtWidgets.QMessageBox.Yes:
                tmp_asset_yml.write("    roughness_invert: True\n")
        else:
            tmp_asset_yml.write("    roughness_invert: False\n")

        tmp_asset_yml.write("    normal_tex: {}\n".format(self.normal_mat_le.text()))
        tmp_asset_yml.write("    opacity_tex: {}\n".format(self.opacity_mat_le.text()))
        tmp_asset_yml.write("    metallic_tex: {}\n".format(self.metal_mat_le.text()))
        tmp_asset_yml.write("    displacement_tex: {}\n".format(self.disp_mat_le.text()))
        tmp_asset_yml.close()
        return tmp_asset_yml_path

    def delete_tmp_data(self):
        tmp_asset_yml_path = r'F:\share\tools\core\maya_core\asset_builder\tmp\{}.yml'.format(self.asset_name_le.text())
        os.remove(tmp_asset_yml_path)

    def build_asset(self):
        if not self.valid_asset_name:
            QtWidgets.QMessageBox.critical(self, "Error",
                                           "Invalid Asset Name! Only alphabetical caharacters and '_' allowed")
            return

        if self.asset_type_dd.currentText() == 'Model' and not self.valid_mesh:
            QtWidgets.QMessageBox.critical(self, "Error", "Please select a valid mesh")
            return

        if self.asset_type_dd.currentText() == 'Material' and self.mat_drop_down.currentText() == 'None':
            QtWidgets.QMessageBox.critical(self, "Error",
                                           "'Material' asset type cannot be built with 'None' material type.")
            return

        if self.mat_drop_down.currentText() != 'None':
            paths = []

            for le in self.texture_line_edits:
                paths.append(le.text())

            ele = paths[0]
            chk = True

            for item in paths:
                if ele != item:
                    chk = False
                    break;

            if chk:
                QtWidgets.QMessageBox.critical(self, "Error",
                                               "No textures selected. Select material type 'None' if asset does not have any textures")
                return
            else:
                pass

        reload(asset)

        asset_name = self.asset_name_le.text()

        if 'Model' in str(self.asset_type_dd.currentText()):
            asset_type = 'model'
        else:
            asset_type = 'material'

        self.write_temp_data()

        tmp_asset_yml_path = r'F:\share\tools\core\maya_core\asset_builder\tmp\{}.yml'.format(self.asset_name_le.text())
        new_asset = asset.Asset(asset_name, asset_type, tmp_asset_yml_path)
        new_asset.create_asset()

        root_path = new_asset.asset_root_path
        self.delete_tmp_data()

        self.close()
        self.validate_asset_name()
        self.show()

    def validate_asset_name(self):
        library_path = r'F:\share\assets\libraries\{0}'.format(self.asset_type_dd.currentText().lower())
        assets = []

        for path in os.listdir(library_path):
            asset_name = path.split('_root')[0]
            assets.append(asset_name)

        if not re.search(r'\w', self.asset_name_le.text()) or re.search(r'\s', self.asset_name_le.text()) or re.search(
                r'\W', self.asset_name_le.text()) or re.search(r'^\d', self.asset_name_le.text()):
            self.asset_name_le.setStyleSheet("color: red;")
            self.valid_asset_name = False
        else:
            if self.asset_name_le.text() in assets:
                self.asset_name_le.setStyleSheet("color: red;")
                self.valid_asset_name = False
            else:
                self.asset_name_le.setStyleSheet("")
                self.valid_asset_name = True


if __name__ == "maya_core.asset_builder.asset_builder_ui" or __name__ == "__main__":
    try:
        asset_builder_dialog.close()  # pylint: disable=E0601
        asset_builder_dialog.deleteLater()
    except:
        pass

    asset_builder_dialog = BuilderWindow()
    asset_builder_dialog.show()
