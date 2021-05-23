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
from maya_core.asset_manager import texture_manager
from maya_core.asset_manager import asset

reload(asset)
reload(texture_manager)

log = logger.Logger()

LIBRARIES_ROOT = "F:\\share\\assets\\libraries\\"

LIBRARIES = OrderedDict()

LIBRARIES["model"] = "F:\\share\\assets\\libraries\\model"
LIBRARIES["material"] = "F:\\share\\assets\\libraries\\material"
LIBRARIES["hdri"] = "F:\\share\\assets\\libraries\\hdri"
LIBRARIES["studio_lights"] = "F:\\share\\assets\\libraries\\studiolights"
LIBRARIES["clouds"] = "F:\\share\\assets\\libraries\\clouds"
LIBRARIES["rigs"] = "F:\\share\\assets\\libraries\\rigs"
LIBRARIES["plants"] = "F:\\share\\assets\\libraries\\plants"

NORMAL_LIBRARIES = ['model',
                    'material',
                    'rigs',
                    'plants']


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
    def __init__(self, asset_name, asset_type, selection=False, preview_image=None, create_proxy=False):
        self.name = asset_name
        self.type = asset_type
        self.selection = selection
        self.preview_image = preview_image
        self.proxy = create_proxy

        self.asset_root_path = 'F:\\share\\assets\\libraries\\{0}\\{1}_root'.format(self.type, self.name)
        self.asset = asset.Asset(path=self.asset_root_path)

        self.maya_path = self.asset_root_path + "\\maya\\{}.ma".format(self.name)

        self.create_folders()
        self.publish_file()
        self.debug = False

    def create_folders(self):
        os.mkdir(self.asset_root_path)
        os.mkdir(self.asset_root_path + "\\textures")
        os.mkdir(self.asset_root_path + "\\maya")

        if self.proxy:
            os.mkdir(self.asset_root_path + "\\vrayproxy")

    def publish_textures(self):
        if self.selection and self.asset:
            mat_data = texture_manager.get_mat_data(cmds.ls(sl=1))

            texture_manager.publish_textures(self.asset, mat_data)

    def publish_file(self):
        if self.selection:
            selection = cmds.ls(sl=True)
            self.obj_selection = selection

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

        if self.proxy:
            self.create_vrayproxy()

    def create_vrayproxy(self):
        proxy_path = self.asset_root_path + "\\vrayproxy"
        proxy_maya_path = proxy_path + "\\{0}_vrayproxy.ma".format(self.name)

        pm.select(self.obj_selection)

        # store shader
        cmds.hyperShade(shaderNetworksSelectMaterialNodes=1)
        material_selection = cmds.ls(sl=1)

        cmds.select(clear=True)
        pm.select(self.obj_selection)

        # export proxy
        cmds.vrayCreateProxy(exportType=1, previewFaces=17500, dir=proxy_path, fname=self.name + ".vrmesh",
                             overwrite=True,
                             previewType="clustering", makeBackup=True, ignoreHiddenObjects=False, vertexColorsOn=True,
                             exportHierarchy=True, includeTransformation=True)

        # deslect everything
        cmds.select(clear=True)

        # create vray_proxy nodes
        vrmesh = self.name + "_vrmesh"
        vraymeshmtl = vrmesh + "_vraymeshmtl"
        vrproxy_path = proxy_path + "\\{}.vrmesh".format(self.name)

        cmds.vrayCreateProxy(createProxyNode=True, node=vrmesh, existing=True,
                             dir=vrproxy_path, geomToLoad=3, newProxyNode=False)

        # assign shader

        cmds.connectAttr("{}.outColor".format(material_selection[0]), "{}.shaders[0]".format(vraymeshmtl))

        # select vray_proxy
        cmds.select(clear=True)

        # save selection as new maya file
        pm.select(vrmesh, r=1)
        pm.exportSelected(proxy_maya_path, type="mayaAscii", channels=True, force=True)


def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class PublishAssetWindow(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(PublishAssetWindow, self).__init__(parent)

        self.setWindowTitle("Publish asset")
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

        self.asset_name_lbl = QtWidgets.QLabel('asset Name')
        self.asset_name_le = QtWidgets.QLineEdit()
        self.asset_name_le.setMinimumWidth(300)

        self.asset_preview_lbl = QtWidgets.QLabel('Preview Image')
        self.asset_preview_le = QtWidgets.QLineEdit()
        self.asset_preview_btn = QtWidgets.QPushButton()
        self.asset_preview_btn.setIcon(file_browse_icon)

        self.asset_type_lbl = QtWidgets.QLabel('asset Type:')
        self.asset_type_dd = QtWidgets.QComboBox()
        self.asset_type_dd.addItems(['model', 'material', 'rigs', 'plants'])

        self.publish_selection_cb = QtWidgets.QCheckBox('Publish Selection')
        self.create_proxy_cb = QtWidgets.QCheckBox('Create Proxy')

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
        btn_layout.addWidget(self.create_proxy_cb)
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
        proxy = self.create_proxy_cb.isChecked()

        asset_publisher = AssetPublisher(self.asset_name_le.text(), self.asset_type_dd.currentText(), selection,
                                         self.asset_preview_le.text(), proxy)

        self.maya_path = asset_publisher.maya_path

        self.publish_confirm()
        self.validate_asset_name()

        asset_manager.build_asset_library()

    def publish_confirm(self):
        if os.path.isfile(self.maya_path):
            message = "asset {} published successfully".format(self.asset_name_le.text())
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


def main():
    try:
        publish_dialog.close()  # pylint: disable=E0601
        publish_dialog.deleteLater()
    except:
        pass

    publish_dialog = PublishAssetWindow()
    publish_dialog.show()


if __name__ == "__main__":
    main()
