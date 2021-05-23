from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import os

import maya.cmds as cmds
import pymel.core as pm

from pyqt_commons import MWidgets
from maya_core.common_tools.logger import Logger

log = Logger()


class VRayProxyUI(QtWidgets.QMainWindow):
    def __init__(self, parent=MWidgets.maya_main_window()):
        super(VRayProxyUI, self).__init__(parent)

        self.setWindowTitle("Create VRay Proxy")
        self.setObjectName("VRayProxyUI")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.setMinimumSize(500, 100)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.asset_root_lbl = QtWidgets.QLabel("asset root:  ")
        self.asset_root_le = QtWidgets.QLineEdit()

        file_browse_icon = QtGui.QIcon(':fileOpen.png')
        self.browse_btn = QtWidgets.QPushButton()
        self.browse_btn.setIcon(file_browse_icon)

        self.create_proxy_btn = QtWidgets.QPushButton("Create Proxy")

    def create_layout(self):
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)

        search_layout = QtWidgets.QHBoxLayout()
        search_layout.addWidget(self.asset_root_lbl)
        search_layout.addWidget(self.asset_root_le)
        search_layout.addWidget(self.browse_btn)

        main_layout.addLayout(search_layout)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.create_proxy_btn)

        main_layout.addLayout(btn_layout)

    def create_menu(self):
        self.menu_bar = QtWidgets.QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        file_menu = QtWidgets.QMenu("File", self)
        edit_menu = QtWidgets.QMenu("Edit", self)
        tools_menu = QtWidgets.QMenu("Tools", self)
        help_menu = QtWidgets.QMenu("Help", self)

        self.menu_bar.addMenu(file_menu)
        self.menu_bar.addMenu(edit_menu)
        self.menu_bar.addMenu(tools_menu)
        self.menu_bar.addMenu(help_menu)

    def create_connections(self):
        self.create_proxy_btn.clicked.connect(self.create_proxy)
        self.browse_btn.clicked.connect(self.browse_path)

    def browse_path(self):
        library_path = "F:\\share\\assets\\libraries\\"

        asset_path = QtWidgets.QFileDialog.getExistingDirectory(MWidgets.maya_main_window(), 'asset Root', library_path)

        self.asset_root_le.setText(asset_path)

    def create_proxy(self):
        create_vrayproxy(self.asset_root_le.text())
        self.close()


def create_vrayproxy(asset_path):
    proxy_path = os.path.join(asset_path, "vrayproxy")
    name = proxy_path.split("/")[-1].split("_root")[0]

    # Override
    if not os.path.isdir(proxy_path):
        os.mkdir(proxy_path)

    proxy_maya_path = proxy_path + "\\{0}_vrayproxy.ma".format(name)

    obj_selection = pm.ls(sl=True)

    pm.select(obj_selection)

    # store shader
    cmds.hyperShade(shaderNetworksSelectMaterialNodes=1)
    material_selection = cmds.ls(sl=1)

    print material_selection

    cmds.select(clear=True)
    pm.select(obj_selection)

    # export proxy
    cmds.vrayCreateProxy(exportType=1, previewFaces=17500, dir=proxy_path, fname=name + ".vrmesh",
                         overwrite=True,
                         previewType="clustering", makeBackup=True, ignoreHiddenObjects=False, vertexColorsOn=True,
                         exportHierarchy=True, includeTransformation=True)

    # deslect everything
    cmds.select(clear=True)

    # create vray_proxy nodes
    vrmesh = name + "_vrmesh"
    vraymeshmtl = vrmesh + "_vraymeshmtl"
    vrproxy_path = proxy_path + "\\{}.vrmesh".format(name)

    cmds.vrayCreateProxy(createProxyNode=True, node=vrmesh, existing=True,
                         dir=vrproxy_path, geomToLoad=3, newProxyNode=False)

    # assign shader

    for i, mat in enumerate(material_selection):
        if "displacement" in mat:
            continue

        cmds.connectAttr("{}.outColor".format(mat), "{0}.shaders[{1}]".format(vraymeshmtl, i))

    # select vray_proxy
    cmds.select(clear=True)

    # save selection as new maya file
    pm.select(vrmesh, r=1)
    pm.exportSelected(proxy_maya_path, type="mayaAscii", channels=True, force=True)

    if os.path.isfile(vrproxy_path):
        log.result("Created vrayproxy successfully")

    if os.path.isfile(proxy_maya_path):
        log.result("Created maya file successfully")


def main():
    try:
        cmds.deleteUI("VRayProxyUI")
    except Exception:
        pass


    dialog = VRayProxyUI()
    dialog.show()


if __name__ == "__main__":
    main()
