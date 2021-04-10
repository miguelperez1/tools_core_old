import os
import re
import subprocess
from shutil import copyfile
from collections import OrderedDict, defaultdict

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import maya.cmds as cmds
import pymel.core as pm

from maya_core import asset_manager

from maya_core.common_tools import logger

log = logger.Logger()


class RecursiveNodeSearch(object):
    def _traverse(self, node, children):

        connections = cmds.listConnections(
            node,
            source=True,
            destination=False,
            skipConversionNodes=True) or {}

        for child in connections:
            children[child] = {}

    def get_nodes(self, node, children):
        self._traverse(node, children)

        for child in children:
            self._traverse(child, children[child])

    def search_nodes(self, node):
        children = {}
        self.get_nodes(node, children)

        return children


class AssetPublisher(object):
    def __init__(self, asset_name, asset_type, selection=False, preview_image=None):
        self.name = asset_name
        self.type = asset_type
        self.selection = selection
        self.preview_image = preview_image

        self.asset_root_path = 'F:\\share\\assets\\libraries\\{0}\\{1}_root'.format(self.type, self.name)

        self.maya_path = self.asset_root_path + "\\maya\\{}.ma".format(self.name)

        self.create_folders()
        self.publish_file()
        self.debug = False

    def create_folders(self):
        os.mkdir(self.asset_root_path)
        os.mkdir(self.asset_root_path + "\\textures")
        os.mkdir(self.asset_root_path + "\\maya")

    def publish_textures(self):

        mat_data = defaultdict(list)

        if self.selection:
            search = RecursiveNodeSearch()

            for obj in cmds.ls(sl=True):
                cmds.hyperShade(shaderNetworksSelectMaterialNodes=1)
                material_selection = cmds.ls(sl=1)
                for mat in material_selection:
                    mat_tex_dst = self.asset_root_path + "\\textures\\" + mat
                    os.mkdir(mat_tex_dst)

                    connections = cmds.listConnections(mat)

                    textures_tmp = []

                    for c in connections:
                        nodes = search.search_nodes(c)
                        for n in nodes:
                            if cmds.nodeType(n) == "file":
                                textures_tmp.append(n)

                    textures = list(set(textures_tmp))

                    mat_data[mat_tex_dst].append(textures)

        if len(mat_data.keys()) > 0:
            for mat_tex_src, texture_lists in mat_data.items():
                for textures in texture_lists:
                    for tex in textures:
                        tex_src_path = cmds.getAttr('{}.fileTextureName'.format(tex))
                        tex_name = tex_src_path.split('/')[-1]

                        tex_dst_path = (mat_tex_src + "\\{}".format(tex_name))

                        log.info("copying {0} to {1}".format(tex_src_path, tex_dst_path))

                        try:
                            copyfile(tex_src_path, tex_dst_path)
                            log.info("copied preview successfully")
                        except Exception as e:
                            log.warning("copy preview failed, skipping: {}".format(e))

                        cmds.setAttr("{}.fileTextureName".format(tex), tex_dst_path, type="string")
        else:
            pass

    def publish_file(self):
        if self.selection:
            selection = cmds.ls(sl=True)

        self.publish_textures()

        # Preview image
        if self.preview_image is not None and self.preview_image != '':
            file_ext = self.preview_image.split('.')[-1]
            preview_dst = self.asset_root_path + '\\{0}_preview.{1}'.format(self.name, file_ext)
            copyfile(self.preview_image, preview_dst)

        if self.selection:
            pm.select(selection, r=1)
            pm.exportSelected(self.maya_path, type="mayaAscii", channels=True, force=True)
        else:
            cmds.file(rename=self.maya_path)
            cmds.file(save=True, type='mayaAscii')


def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class PublishAssetWindow(QtWidgets.QDialog):
    """
    Dialog used to demonstrates many of the standard dialogs available in Qt
    """

    def __init__(self, parent=maya_main_window()):
        super(PublishAssetWindow, self).__init__(parent)

        self.setWindowTitle("Publish Asset")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.setMinimumWidth(400)

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        file_browse_icon = QtGui.QIcon(':fileOpen.png')

        self.asset_name_lbl = QtWidgets.QLabel('Asset Name')
        self.asset_name_le = QtWidgets.QLineEdit()
        self.asset_name_le.setMinimumWidth(300)

        self.asset_preview_lbl = QtWidgets.QLabel('Preview Image')
        self.asset_preview_le = QtWidgets.QLineEdit()
        self.asset_preview_btn = QtWidgets.QPushButton()
        self.asset_preview_btn.setIcon(file_browse_icon)

        self.asset_type_lbl = QtWidgets.QLabel('Asset Type:')
        self.asset_type_dd = QtWidgets.QComboBox()
        self.asset_type_dd.addItems(['model', 'material', 'rigs', 'plants'])

        self.publish_selection_cb = QtWidgets.QCheckBox('Publish Selection')

        self.build_btn = QtWidgets.QPushButton("Publish")

        self.debug_mode_cb = QtWidgets.QCheckBox("Debug Mode")

    def create_layout(self):
        name_layout = QtWidgets.QHBoxLayout()
        name_layout.addWidget(self.asset_name_lbl)
        name_layout.addWidget(self.asset_name_le)
        name_layout.addStretch()

        type_layout = QtWidgets.QHBoxLayout()
        type_layout.addWidget(self.asset_type_lbl)
        type_layout.addWidget(self.asset_type_dd)
        type_layout.addStretch()

        preview_layout = QtWidgets.QHBoxLayout()
        preview_layout.addWidget(self.asset_preview_lbl)
        preview_layout.addWidget(self.asset_preview_le)
        preview_layout.addWidget(self.asset_preview_btn)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.publish_selection_cb)
        btn_layout.addWidget(self.debug_mode_cb)
        btn_layout.addStretch()
        btn_layout.addWidget(self.build_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(name_layout)
        main_layout.addLayout(type_layout)
        main_layout.addLayout(preview_layout)
        main_layout.addLayout(btn_layout)

    def create_connections(self):
        self.asset_preview_btn.clicked.connect(self.browse_preview)
        self.build_btn.clicked.connect(self.publish_asset)
        self.asset_name_le.textChanged.connect(self.validate_asset_name)
        self.debug_mode_cb.stateChanged.connect(self.debug_mode_cb_callback)

    def debug_mode_cb_callback(self):
        log.status = self.debug_mode_cb.isChecked()

    def publish_asset(self):
        if not self.valid_asset_name:
            log.error("Invalid asset name")
            return

        selection = self.publish_selection_cb.isChecked()

        asset_publisher = AssetPublisher(self.asset_name_le.text(), self.asset_type_dd.currentText(), selection,
                                         self.asset_preview_le.text())

        self.maya_path = asset_publisher.maya_path

        self.publish_confirm()
        self.validate_asset_name()

        asset_manager.build_asset_library()

    def publish_confirm(self):
        if os.path.isfile(self.maya_path):
            message = "Asset {} published successfully".format(self.asset_name_le.text())
            log.result(message)

    def browse_preview(self):
        file_name = QtWidgets.QFileDialog.getOpenFileName(self, 'Select Preview Image')[0]
        if file_name.endswith('png') or file_name.endswith('jpg') or file_name.endswith('jpeg'):
            self.asset_preview_le.setText(file_name)
        else:
            return

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


if __name__ == "__main__" or __name__ == "maya_core.asset_manager.publish_asset.publish_asset":

    try:
        publish_dialog.close()  # pylint: disable=E0601
        publish_dialog.deleteLater()
    except:
        pass

    publish_dialog = PublishAssetWindow()
    publish_dialog.show()
