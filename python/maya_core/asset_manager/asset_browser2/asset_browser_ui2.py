import os
from collections import OrderedDict
import operator
import json
import subprocess
from shutil import copyfile
import re
import imagesize

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm

from pyqt_commons import MWidgets

from maya_core.common_tools import yaml_reader
from maya_core.common_tools import logger

reload(logger)

LIBRARIES_ROOT = "F:\\share\\assets\\libraries\\"

LIBRARIES = OrderedDict()

LIBRARIES["model"] = "F:\\share\\assets\\libraries\\model"
LIBRARIES["material"] = "F:\\share\\assets\\libraries\\material"
LIBRARIES["hdri"] = "F:\\share\\assets\\libraries\\hdri"
LIBRARIES["studio_lights"] = "F:\\share\\assets\\libraries\\studiolights"
LIBRARIES["gobo_lights"] = "F:\\share\\assets\\libraries\\gobolights"
LIBRARIES["clouds"] = "F:\\share\\assets\\libraries\\clouds"
LIBRARIES["rigs"] = "F:\\share\\assets\\libraries\\rigs"
LIBRARIES["plants"] = "F:\\share\\assets\\libraries\\plants"

NORMAL_LIBRARIES = ['model',
                    'material',
                    'rigs',
                    'plants']


class AssetBrowserWindow(QtWidgets.QMainWindow):
    push_log = QtCore.Signal(str, str)
    light_created = QtCore.Signal(str)

    def __init__(self, parent=MWidgets.maya_main_window()):
        super(AssetBrowserWindow, self).__init__(parent)

        self.setWindowTitle("Asset Browser 2")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.setObjectName("AssetBrowserWindow")

        self.width = 1700
        self.height = 900

        self.setMinimumSize(self.width, self.height)

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.current_library = None
        self.current_tag = None

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        # Default Actions
        self.open_action = QtWidgets.QAction("Open", self)
        self.open_root_action = QtWidgets.QAction("Open in Explorer", self)
        self.open_preview_action = QtWidgets.QAction("Open Preview", self)
        self.replace_preview_action = QtWidgets.QAction('Replace Preview', self)

        # Common Actions
        self.import_action = QtWidgets.QAction("Import", self)
        self.reference_action = QtWidgets.QAction("Reference", self)
        self.import_proxy_action = QtWidgets.QAction("Import VRay Proxy", self)

        # Material Actions
        self.material_import_assign_action = QtWidgets.QAction('Import and assign to selected', self)

    def create_widgets(self):
        # Search Bar
        self.search_lbl = QtWidgets.QLabel("Search Assets")
        self.search_le = QtWidgets.QLineEdit()

        # Filter TW
        self.filter_tw = QtWidgets.QTreeWidget()
        header_item = QtWidgets.QTreeWidgetItem(['Libraries'])
        self.filter_tw.setHeaderItem(header_item)

        self.refresh_filter_tw()

        # Assets TW
        self.assets_tw = QtWidgets.QTreeWidget()
        asset_header_item = QtWidgets.QTreeWidgetItem(['Preview', 'Name'])
        self.assets_tw.setHeaderItem(asset_header_item)
        self.assets_tw.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.assets_tw.setAlternatingRowColors(True)

        # Properties Container
        self.properties_widget = QtWidgets.QWidget()
        self.prop_name_lbl = QtWidgets.QLabel("Asset Name: ")
        self.prop_tags_lbl = QtWidgets.QLabel("Tags: ")
        self.prop_tags_le = QtWidgets.QLineEdit()
        self.prop_tags_save_btn = QtWidgets.QPushButton("Save Tags")
        self.prop_icon = MWidgets.PreviewLabel()

        prop_layout = QtWidgets.QVBoxLayout(self.properties_widget)

        prop_layout.addWidget(self.prop_name_lbl)
        prop_layout.addSpacing(10)

        icon_layout = QtWidgets.QHBoxLayout()
        icon_layout.addStretch()
        icon_layout.addWidget(self.prop_icon)
        icon_layout.addStretch()

        prop_layout.addLayout(icon_layout)

        tags_layout = QtWidgets.QHBoxLayout()
        tags_layout.addWidget(self.prop_tags_lbl)
        tags_layout.addWidget(self.prop_tags_le)
        tags_layout.addWidget(self.prop_tags_save_btn)

        prop_layout.addLayout(tags_layout)
        prop_layout.addStretch()

        # Logger
        self.log_widget = logger.LogWidget()

        # Resize
        self.filter_tw.setMaximumWidth(self.width * .15)
        self.assets_tw.setMinimumWidth(self.width * .5)
        self.properties_widget.setMaximumWidth(self.width * .35)

    def create_layout(self):
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)

        main_layout.addSpacing(10)

        search_layout = QtWidgets.QHBoxLayout()
        search_layout.addWidget(self.search_lbl)
        search_layout.addWidget(self.search_le)

        main_layout.addLayout(search_layout)
        main_layout.addWidget(MWidgets.QHLine())
        main_layout.addSpacing(10)

        tw_layout = QtWidgets.QHBoxLayout()

        tw_layout.addWidget(self.filter_tw)
        tw_layout.addWidget(MWidgets.QVLine())
        tw_layout.addWidget(self.assets_tw)
        tw_layout.addWidget(MWidgets.QVLine())
        tw_layout.addWidget(self.properties_widget)

        main_layout.addLayout(tw_layout)
        main_layout.addWidget(self.log_widget)

    def create_connections(self):
        self.search_le.textChanged.connect(self.filter_by_search)
        self.filter_tw.currentItemChanged.connect(self.refresh_assets)
        self.assets_tw.currentItemChanged.connect(self.refresh_properties)
        self.prop_tags_save_btn.clicked.connect(self.save_tags)

        self.assets_tw.customContextMenuRequested.connect(self.show_asset_context_menu)

        # Default Actions
        self.open_action.triggered.connect(self.open_action_callback)
        self.open_root_action.triggered.connect(self.open_root_action_callback)
        self.replace_preview_action.triggered.connect(self.replace_preview_action_callback)
        self.open_preview_action.triggered.connect(self.open_preview_action_callback)

        # Common Actions
        self.import_action.triggered.connect(self.import_action_callback)
        self.reference_action.triggered.connect(self.reference_action_callback)
        self.import_proxy_action.triggered.connect(self.import_proxy_action_callback)

        # Material Actions
        self.material_import_assign_action.triggered.connect(self.material_import_assign_action_callback)

        self.push_log.connect(self.update_log)

    def refresh_filter_tw(self):
        self.filter_tw.blockSignals(True)
        self.filter_tw.clear()

        for library in LIBRARIES:
            library_path = LIBRARIES[library]

            library_item = QtWidgets.QTreeWidgetItem()
            library_item.setText(0, library.title())
            library_item.setChildIndicatorPolicy(QtWidgets.QTreeWidgetItem.DontShowIndicatorWhenChildless)

            self.filter_tw.addTopLevelItem(library_item)

            library_tags = self.get_library_tags(library_path)

            for tag in library_tags:
                tag_item = QtWidgets.QTreeWidgetItem()
                tag_item.setText(0, tag.title())

                library_item.addChild(tag_item)

        self.filter_tw.blockSignals(False)

    def refresh_assets(self, item):
        self.assets_tw.blockSignals(True)

        if item.parent() is not None:
            self.current_library = item.parent().text(0).lower()
            self.current_tag = item.text(0)
        else:
            self.current_library = item.text(0).lower()
            self.current_tag = None

        self.assets_tw.clear()

        library_path = LIBRARIES[self.current_library]

        library_yml = library_path + "\\library.yml"

        data = yaml_reader.read_yaml(library_yml)

        library_data = sorted(data.items(), key=operator.itemgetter(0))

        for asset_data in library_data:
            asset = asset_data[0]
            preview_path = asset_data[1]

            if self.current_library in NORMAL_LIBRARIES:
                asset_path = os.path.join(library_path, "{}_root".format(asset))
                asset_json_path = os.path.join(asset_path, "data.json")

                json_file = open(asset_json_path, "r")
                asset_data = json.load(json_file)
                json_file.close()

                if self.current_tag:
                    if not self.current_tag.lower() in asset_data["tags"].split(","):
                        continue

            icon_widget = MWidgets.PreviewLabel()
            icon_widget.setContentsMargins(5, 5, 5, 5)
            icon_widget.setAccessibleName(asset)
            icon_widget.setToolTip(icon_widget.accessibleName())
            icon_widget.setObjectName(preview_path)

            asset_item_size = 125

            if os.path.isfile(preview_path):
                icon_widget.set_image(preview_path, asset_item_size)
            else:
                icon_widget.set_default()

            asset_item = QtWidgets.QTreeWidgetItem()
            asset_item.setText(1, asset)
            asset_item.setSizeHint(0, QtCore.QSize(asset_item_size * 1.1, asset_item_size * 1.1))

            if self.current_library in NORMAL_LIBRARIES:
                asset_item.setData(0, QtCore.Qt.UserRole, asset_json_path)

            self.assets_tw.addTopLevelItem(asset_item)
            self.assets_tw.setItemWidget(asset_item, 0, icon_widget)

        self.assets_tw.blockSignals(False)

        self.assets_tw.resizeColumnToContents(0)

        if self.current_tag:
            self.push_log.emit("result",
                               "Assets loaded for {0} library, using {1} tag".format(self.current_library.title(),
                                                                                     self.current_tag))
        else:
            self.push_log.emit("result", "Assets loaded for {} library".format(self.current_library.title()))

    def refresh_properties(self, asset_item):
        self.assets_tw.blockSignals(True)

        self.current_asset = asset_item.text(1)
        self.current_asset_item = asset_item

        asset_path = os.path.join(LIBRARIES[self.current_library], "{}_root".format(self.current_asset))

        asset_data_file = os.path.join(asset_path, "data.json")

        self.prop_name_lbl.setText("Asset Name: " + self.current_asset)

        if os.path.isfile(asset_data_file):
            with open(asset_data_file, "r+") as file:
                data = json.load(file)
                if data:
                    tags = data["tags"]
                    self.prop_tags_le.setText(tags)
                    self.prop_tags_le.setEnabled(True)

                    if data["preview"]:
                        self.prop_icon.set_image(data["preview"], 350)
        else:
            preview_path_tmp = os.path.join(LIBRARIES[self.current_library], "thumbnails",
                                            "{}_preview.png".format(self.current_asset))

            preview_path = preview_path_tmp.replace(".hdr", "").replace(".tif", "").replace(".tiff", "").replace(".exr",
                                                                                                                 "")

            if os.path.isfile(preview_path):
                self.prop_icon.set_image(preview_path, 325)
            else:
                self.push_log.emit("warning", "Preview path {} does not exist".format(preview_path))

            self.prop_tags_le.setText("Tags not enabled for lights and vbds")
            self.prop_tags_le.setEnabled(False)

        self.assets_tw.blockSignals(False)

    def save_tags(self):
        asset_path = os.path.join(LIBRARIES[self.current_library], "{}_root".format(self.current_asset))
        asset_data_file = os.path.join(asset_path, "data.json")

        json_file = open(asset_data_file, "r")
        data = json.load(json_file)
        json_file.close()

        data["tags"] = self.prop_tags_le.text()

        json_file = open(asset_data_file, "w")
        json.dump(data, json_file, indent=4, sort_keys=True)
        json_file.close()

        self.refresh_filter_tw()

        self.push_log.emit("result", "Saved tags for {0}. Tags saved: {1}".format(self.current_asset, ", ".join(
            self.prop_tags_le.text().split(","))))

    def get_library_tags(self, library_path):
        all_tags = []

        for asset in os.listdir(library_path):
            asset_data_json = os.path.join(library_path, asset, "data.json")

            if os.path.isfile(asset_data_json):
                json_file = open(asset_data_json, "r")
                asset_data = json.load(json_file)
                json_file.close()

                tags = asset_data["tags"].split(",")

                for tag in tags:
                    if tag and tag not in all_tags:
                        all_tags.append(tag)

        return sorted(all_tags)

    def show_asset_context_menu(self, eventPosition):
        asset_item = self.assets_tw.itemAt(eventPosition)
        asset = asset_item.text(1)

        contextMenu = QtWidgets.QMenu(self)

        self.about_action = QtWidgets.QAction(asset)
        contextMenu.addAction(self.about_action)

        contextMenu.addSeparator()

        contextMenu.addAction(self.open_action)
        contextMenu.addAction(self.replace_preview_action)
        contextMenu.addAction(self.open_preview_action)
        contextMenu.addAction(self.open_root_action)

        contextMenu.addSeparator()

        contextMenu.addAction(self.import_action)

        if self.current_library in NORMAL_LIBRARIES:
            contextMenu.addAction(self.reference_action)

            asset_path = LIBRARIES[self.current_library] + "\\{}_root".format(self.current_asset)

            if "vrayproxy" in os.listdir(asset_path):
                contextMenu.addAction(self.import_proxy_action)

        contextMenu.addSeparator()

        if self.current_library == "material":
            contextMenu.addAction(self.material_import_assign_action)

        action = contextMenu.exec_(self.assets_tw.mapToGlobal(eventPosition))

    def open_action_callback(self):
        library_path = LIBRARIES_ROOT + "" + self.current_library
        maya_path = library_path + "\\{0}_root\\maya\\{0}.ma".format(self.current_asset)
        os.startfile(maya_path)

    def open_root_action_callback(self):
        library_path = LIBRARIES_ROOT + "\\" + self.current_library
        if self.current_library in NORMAL_LIBRARIES:
            root_path = os.path.join(library_path.replace("\\\\", "\\"), "{0}_root".format(self.current_asset))
        else:
            root_path = LIBRARIES[self.current_library]

        subprocess.Popen('explorer "{}"'.format(root_path))

    def replace_preview_action_callback(self):
        dst = self.current_preview_path
        src = QtWidgets.QFileDialog.getOpenFileName(self, 'Select New Preview Image')[0]

        copyfile(src, dst)

    def open_preview_action_callback(self):
        os.system("start " + self.current_preview_path)

    def import_action_callback(self):
        if self.current_library in NORMAL_LIBRARIES:
            library_path = LIBRARIES_ROOT + "\\" + self.current_library
            tmp_path = library_path + "\\{0}_root\\maya\\{0}.ma".format(self.current_asset)

            if os.path.isfile(tmp_path):
                maya_path = tmp_path
            elif os.path.isfile(tmp_path.replace('.ma', '.mb')):
                maya_path = tmp_path.replace('.ma', '.mb')

            cmds.file(maya_path, i=True)

        elif self.current_library == "studio_lights":
            self.import_studio_light()
        elif self.current_library == "gobo_lights":
            self.import_gobo_light()
        elif self.current_library == "hdri":
            self.import_hdr()
        elif self.current_library == "clouds":
            self.import_cloud()

        self.push_log.emit("result", "Imported {}".format(self.current_asset))

    def reference_action_callback(self):
        if self.current_library in NORMAL_LIBRARIES:
            library_path = LIBRARIES_ROOT + "\\" + self.current_library
            tmp_path = library_path + "\\{0}_root\\maya\\{0}.ma".format(self.current_asset)

            if os.path.isfile(tmp_path):
                maya_path = tmp_path
            elif os.path.isfile(tmp_path.replace('.ma', '.mb')):
                maya_path = tmp_path.replace('.ma', '.mb')

            cmds.file(maya_path, reference=True)

            self.push_log.emit("result", "Referenced {}".format(self.current_asset))

    def material_import_assign_action_callback(self):
        library_path = LIBRARIES_ROOT + "\\" + self.current_library
        maya_path = library_path + "\\{0}_root\\maya\\{0}.ma".format(self.current_asset)

        shading_group = None

        selected = cmds.ls(sl=True)

        cmds.file(maya_path, i=True)

        for sg in cmds.ls(type="shadingEngine"):
            if re.search("^" + self.current_asset + ".*_sg$|^" + self.current_asset + ".*_shading_group", sg):
                shading_group = sg
                break

        for node in selected:
            if shading_group is not None:
                cmds.sets(node, e=True, forceElement=shading_group)

        self.push_log.emit("result", "Imported {}".format(self.current_asset))

    def import_proxy_action_callback(self):
        proxy_path = os.path.join(LIBRARIES[self.current_library], "{}_root".format(self.current_asset), "vrayproxy",
                                  "{}_vrayproxy.ma".format(self.current_asset))

        if os.path.isfile(proxy_path):
            cmds.file(proxy_path, i=True)

    def update_log(self, message_type, message):
        getattr(self.log_widget, message_type)(message)

    def filter_by_search(self):
        search_filter = self.search_le.text().lower()

        for i in range(self.assets_tw.topLevelItemCount()):
            item = self.assets_tw.topLevelItem(i)

            if self.current_library in NORMAL_LIBRARIES:
                asset_json_path = item.data(0, QtCore.Qt.UserRole)

                json_file = open(asset_json_path, "r")
                asset_data = json.load(json_file)
                json_file.close()

            # if search_filter.startswith("tag:"):
            #     if not re.search(self.search_le.text().split("tag:")[-1], asset_data["tags"]):
            #         item.setHidden(True)

            if not re.search(self.search_le.text(), item.text(1).lower()):
                item.setHidden(True)
            else:
                item.setHidden(False)

    def import_studio_light(self):
        path = LIBRARIES['studio_lights'] + '\\{}'.format(self.current_asset)
        area_trans = cmds.createNode('transform', n='l_{}'.format(self.current_asset[:-4]))
        lgt = cmds.shadingNode('VRayLightRectShape', n=area_trans + "Shape", p=area_trans, asLight=True)

        cmds.setAttr('{}.useRectTex'.format(lgt), 1)
        mel.eval('sets -edit -forceElement defaultLightSet {} ;'.format(lgt))
        tex = cmds.shadingNode('file', asTexture=True, isColorManaged=True)
        cmds.connectAttr('{}.outColor'.format(tex), '{}.rectTex'.format(lgt))
        cmds.setAttr('{}.fileTextureName'.format(tex), path, type='string')
        cmds.setAttr('{}.intensityMult'.format(lgt), 1)
        cmds.setAttr('{}.showTex'.format(lgt), 0)
        cmds.setAttr('{}.invisible'.format(lgt), 1)
        cmds.setAttr('{}.multiplyByTheLightColor'.format(lgt), 1)

        aspect_ratio = self.get_preview_size(path)

        cmds.setAttr('{}.scaleY'.format(area_trans), 1 / aspect_ratio)

        light_shape = cmds.listRelatives(lgt, shapes=True)[0]

        self.light_created.emit(lgt)

    def import_gobo_light(self):
        path = LIBRARIES['gobo_lights'] + '\\{}'.format(self.current_asset)

        area_trans = cmds.createNode('transform', n='l_{}'.format(self.current_asset[:-4]))
        lgt = cmds.shadingNode('VRayLightRectShape', n=area_trans + "Shape", p=area_trans, asLight=True)

        cmds.setAttr('{}.useRectTex'.format(lgt), 1)
        mel.eval('sets -edit -forceElement defaultLightSet {} ;'.format(lgt))
        tex = cmds.shadingNode('file', asTexture=True, isColorManaged=True)
        cmds.connectAttr('{}.outColor'.format(tex), '{}.rectTex'.format(lgt))
        cmds.setAttr('{}.fileTextureName'.format(tex), path, type='string')
        cmds.setAttr('{}.intensityMult'.format(lgt), 1)
        cmds.setAttr('{}.showTex'.format(lgt), 1)
        cmds.setAttr('{}.invisible'.format(lgt), 1)
        cmds.setAttr('{}.multiplyByTheLightColor'.format(lgt), 1)
        cmds.setAttr('{}.directional'.format(lgt), .99)

        aspect_ratio = self.get_preview_size(path)

        cmds.setAttr('{}.scaleY'.format(area_trans), 1 / aspect_ratio)

        uv_node = cmds.shadingNode("place2dTexture", name='{}_place2d'.format(self.current_asset[:-4]), asUtility=True)
        cmds.connectAttr('{}.outUV'.format(uv_node), '{}.uvCoord'.format(tex))

        light_shape = cmds.listRelatives(lgt, shapes=True)[0]

        self.light_created.emit(lgt)

    def import_hdr(self):
        path = LIBRARIES['hdri'] + '\\{}'.format(self.current_asset)

        dome_trans = cmds.createNode('transform', n='l_{}'.format(self.current_asset[:-4]))
        lgt = cmds.shadingNode('VRayLightDomeShape', n=dome_trans + "Shape", p=dome_trans, asLight=True)
        mel.eval('sets -edit -forceElement  defaultLightSet {} ;'.format(lgt))

        cmds.setAttr('{}.useDomeTex'.format(lgt), 1)
        cmds.setAttr('{}.invisible'.format(lgt), 1)
        cmds.setAttr('{}.viewportTexEnable'.format(lgt), 0)

        tex = cmds.shadingNode('file', asTexture=True, isColorManaged=True)
        cmds.setAttr('{}.fileTextureName'.format(tex), path, type='string')

        cc_node = cmds.createNode("colorCorrect")
        vray_place_tex = cmds.createNode("VRayPlaceEnvTex")
        cmds.setAttr("{}.useTransform".format(vray_place_tex), 1)
        cmds.setAttr("{}.mappingType".format(vray_place_tex), 2)
        uv_node = cmds.shadingNode("place2dTexture", name='{}_place2d'.format(self.current_asset), asUtility=True)

        cmds.connectAttr("{}.worldMatrix".format(dome_trans), "{}.transform".format(vray_place_tex))
        cmds.connectAttr("{}.uvCoord".format(uv_node), "{}.outUV".format(vray_place_tex))
        cmds.connectAttr("{}.outUV".format(vray_place_tex), "{}.uvCoord".format(tex))

        cmds.connectAttr("{}.outColor".format(tex), "{}.inColor".format(cc_node))
        cmds.connectAttr('{}.outColor'.format(cc_node), '{}.domeTex'.format(lgt))

        light_shape = cmds.listRelatives(lgt, shapes=True)[0]

        self.light_created.emit(lgt)

    def get_preview_size(self, preview_path):
        asset_image_path = preview_path
        image_size = imagesize.get(asset_image_path)
        aspect_ratio = float(float(image_size[0]) / float(image_size[1]))

        return aspect_ratio


def main():
    try:
        cmds.deleteUI("AssetBrowserWindow")
    except Exception:
        pass

    dialog = AssetBrowserWindow()
    dialog.show()


if __name__ == "__main__":
    main()
