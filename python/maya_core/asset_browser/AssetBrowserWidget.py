import os
import re
from collections import OrderedDict
import subprocess
import logging
import json

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import pymel.core as pm

from pyqt_commons import MWidgets
from maya_core.asset_manager.library_utils import library_utils
from maya_core.asset_manager.library_utils import constants
from maya_core.lighting.lighting_utils import lighting_utils
from maya_core.lookdev.material_utils import material_utils

libraries = constants.libraries
logger = logging.getLogger(__name__)
logger.setLevel(10)


class AssetTreeWidget(QtWidgets.QTreeWidget):
    tags_updated = QtCore.Signal()

    def __init__(self):
        super(AssetTreeWidget, self).__init__()
        self.itemDoubleClicked.connect(self.onTreeWidgetItemDoubleClicked)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setAlternatingRowColors(True)

        header_item = QtWidgets.QTreeWidgetItem(['Preview', 'Asset', 'Tags'])
        self.setHeaderItem(header_item)

        self.itemChanged.connect(self.update_tags)

    def onTreeWidgetItemDoubleClicked(self, item, column):
        # Only allow the tags column to be edited
        if column == 2:
            self.editItem(item, column)

    def update_tags(self, item, column):
        data = item.data(0, QtCore.Qt.UserRole)
        asset_name = item.text(1)

        # Update normal asset tags
        if data['asset_type'] in ['model', 'material', 'rigs', 'plants']:
            asset_json_path = os.path.join(libraries[data['asset_type']], data['name'], "data.json")

            if os.path.exists(asset_json_path):
                json_file = open(asset_json_path, "r")
                asset_data = json.load(json_file)
                json_file.close()

                asset_data['tags'] = item.text(2)

                with open(asset_json_path, "w") as f:
                    json.dump(asset_data, f, indent=4, sort_keys=True)

        else:
            library_json_path = os.path.join(libraries[data['asset_type']], "assets.json")
            library_data = library_utils.get_library_data(data['asset_type'])

            asset_data = library_data['assets'][asset_name]

            asset_data['tags'] = item.text(2)

            library_data['assets'][asset_name] = asset_data

            with open(library_json_path, "w") as f:
                json.dump(library_data, f, indent=4, sort_keys=True)

        data['tags'] = item.text(2)

        item.setData(0, QtCore.Qt.UserRole, data)

        library_utils.build_library_jsons(data['asset_type'])

        self.tags_updated.emit()


class AssetBrowserWidget(QtWidgets.QWidget):
    light_created = QtCore.Signal(pm.PyNode)


    def __init__(self, width, height, use_tags_widget=1):
        super(AssetBrowserWidget, self).__init__()
        self.setObjectName("AssetBrowserUI")
        self.size = (width, height)

        self.setMinimumSize(width, height)

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        # Default Actions
        self.open_action = QtWidgets.QAction("Open", self)
        self.open_root_action = QtWidgets.QAction("Open in Explorer", self)

        # Common Actions
        self.import_action = QtWidgets.QAction("Import", self)
        self.reference_action = QtWidgets.QAction("Reference", self)
        self.import_vrayproxy_action = QtWidgets.QAction("Import VRay Proxy", self)

        # Material Actions
        self.material_import_assign_action = QtWidgets.QAction('Import and assign to selected', self)
        self.build_material_action = QtWidgets.QAction("Build Material")
        self.build_and_assign_material_action = QtWidgets.QAction("Build and Assign Material")

        # Texture Actions
        self.create_card_action = QtWidgets.QAction("Create Card")

    def create_widgets(self):
        self.search_lble = MWidgets.LabeledLineEdit('Search')

        self.libraries_tw = QtWidgets.QTreeWidget()
        header_item = QtWidgets.QTreeWidgetItem()
        header_item.setText(0, 'Libraries')
        self.libraries_tw.setHeaderItem(header_item)
        self.libraries_tw.setAlternatingRowColors(True)
        self.libraries_tw.setMaximumWidth(self.width() * .2)

        self.refresh_libraries_tw()

        self.assets_tw = AssetTreeWidget()

        self.assets_tw.setMinimumWidth(self.width() * .8)
        self.assets_tw.setColumnWidth(0, 200)
        self.assets_tw.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.create_asset_item_widgets()

    def refresh_libraries_tw(self):
        self.libraries_tw.blockSignals(True)
        self.libraries_tw.clear()

        item_font = QtGui.QFont()
        item_font.setPointSize(10)

        for library in sorted(libraries.keys()):
            if library == 'root':
                continue

            library_item = QtWidgets.QTreeWidgetItem()
            library_item.setText(0, library.title())
            library_item.setFont(0, item_font)

            library_data = library_utils.get_library_data(library)

            for tag in library_data["tags"]:
                if not tag:
                    continue

                tag_item = QtWidgets.QTreeWidgetItem()
                tag_item.setText(0, tag.title())
                tag_item.setFont(0, item_font)

                library_item.addChild(tag_item)

            self.libraries_tw.addTopLevelItem(library_item)

        self.libraries_tw.blockSignals(False)

    def create_asset_item_widgets(self):
        self.assets_tw.blockSignals(True)

        self.asset_item_widgets = []
        for library in libraries.keys():
            library_data = library_utils.get_library_data(library)

            if not library_data:
                continue

            for k in sorted(library_data["assets"].keys(), key=lambda x: x.lower()):
                asset_data = library_data["assets"][k]

                asset = asset_data["asset_name"]
                preview = asset_data["asset_preview"]

                if "tags" in asset_data.keys():
                    tags = asset_data["tags"]
                else:
                    tags = ""

                preview_widget = MWidgets.PreviewLabel()
                preview_widget.setFixedSize(160, 160)
                preview_widget.set_image(preview, 150)

                new_asset_data = {
                    'name': asset,
                    'asset_type': library,
                    'tags': tags,
                }

                if 'import_file' in asset_data.keys():
                    new_asset_data['import_file'] = asset_data['import_file']
                if 'material_data' in asset_data.keys():
                    new_asset_data['material_data'] = asset_data['material_data']

                asset_item = QtWidgets.QTreeWidgetItem()
                asset_item.setText(1, asset)
                asset_item.setText(2, tags)
                asset_item.setData(0, QtCore.Qt.UserRole, new_asset_data)
                asset_item.setFlags(asset_item.flags() | QtCore.Qt.ItemIsEditable)

                item_font = QtGui.QFont()
                item_font.setPointSize(10)
                asset_item.setFont(1, item_font)
                asset_item.setFont(2, item_font)

                self.assets_tw.addTopLevelItem(asset_item)
                self.assets_tw.setItemWidget(asset_item, 0, preview_widget)
                asset_item.setHidden(True)

                self.asset_item_widgets.append(asset_item)

        self.assets_tw.blockSignals(False)

    def refresh_asset_items(self):
        logger.debug("Refreshing asset items")

        if not self.libraries_tw.selectedItems():
            return

        selected_item = self.libraries_tw.selectedItems()[0]

        if not selected_item.parent():
            self.current_library = selected_item.text(0).lower()
            tag = ''
        else:
            self.current_library = selected_item.parent().text(0).lower()
            tag = selected_item.text(0).lower()

        for asset_item_widget in self.asset_item_widgets:
            asset_data = asset_item_widget.data(0, QtCore.Qt.UserRole)

            if asset_data['asset_type'] == self.current_library:
                asset_item_widget.setHidden(False)

                if tag and tag.lower() not in asset_data['tags'].split(","):
                    asset_item_widget.setHidden(True)

                if self.search_lble.text():
                    if not re.search(self.search_lble.text(), asset_item_widget.text(1)) and not re.search(
                            self.search_lble.text(), asset_data['tags']):
                        asset_item_widget.setHidden(True)

            else:
                asset_item_widget.setHidden(True)

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.addWidget(self.search_lble)

        tw_layout = QtWidgets.QHBoxLayout()
        tw_layout.addWidget(self.libraries_tw)
        tw_layout.addWidget(self.assets_tw)

        main_layout.addLayout(tw_layout)

    def create_connections(self):
        self.libraries_tw.itemSelectionChanged.connect(self.refresh_asset_items)
        self.search_lble.le_widget.textChanged.connect(self.refresh_asset_items)
        self.assets_tw.customContextMenuRequested.connect(self.show_asset_context_menu)
        self.assets_tw.itemSelectionChanged.connect(self.update_current_asset)

        self.open_root_action.triggered.connect(self.open_root_action_callback)
        self.open_action.triggered.connect(self.open_action_callback)
        self.import_action.triggered.connect(self.import_action_callback)
        self.import_vrayproxy_action.triggered.connect(self.import_vrayproxy_action_callback)
        self.build_material_action.triggered.connect(self.build_material_action_callback)
        self.build_and_assign_material_action.triggered.connect(self.build_and_assign_material_action_callback)
        self.create_card_action.triggered.connect(self.create_card_action_callback)

        self.assets_tw.tags_updated.connect(self.refresh_libraries_tw)

    def update_current_asset(self):
        if self.assets_tw.selectedItems():
            self.current_asset_item = self.assets_tw.selectedItems()[0]
            self.current_asset = self.assets_tw.selectedItems()[0].text(1)
            self.current_asset_data = self.current_asset_item.data(0, QtCore.Qt.UserRole)
        else:
            self.current_asset_item = None
            self.current_asset = None
            self.current_asset_data = None

    def show_asset_context_menu(self, eventPosition):
        asset_item = self.assets_tw.itemAt(eventPosition)
        asset = asset_item.text(1)

        contextMenu = QtWidgets.QMenu(self)

        self.about_action = QtWidgets.QAction(asset)
        contextMenu.addAction(self.about_action)

        contextMenu.addSeparator()

        if self.current_library in ['model', 'material', 'rigs', 'plants']:
            contextMenu.addAction(self.open_action)

        contextMenu.addAction(self.import_action)

        if self.current_library in ['model', 'material', 'rigs', 'plants']:
            contextMenu.addAction(self.reference_action)

            asset_path = os.path.join(library_utils.libraries[self.current_library], asset)

            if "vrayproxy" in os.listdir(asset_path):
                contextMenu.addAction(self.import_vrayproxy_action)

        contextMenu.addSeparator()

        if self.current_library == "material":
            contextMenu.addAction(self.build_material_action)
            contextMenu.addAction(self.build_and_assign_material_action)
            # contextMenu.addAction(self.material_import_assign_action)

        if self.current_library == 'texture':
            contextMenu.addSeparator()
            contextMenu.addAction(self.create_card_action)

        contextMenu.addSeparator()

        contextMenu.addAction(self.open_root_action)

        action = contextMenu.exec_(self.assets_tw.mapToGlobal(eventPosition))

    def import_action_callback(self):
        logger.info("Importing %s", self.current_asset)
        logger.debug("Import file %s", self.current_asset_data['import_file'])

        if self.current_library == "studiolights":
            light = lighting_utils.create_vray_light("VRayLightRectShape", name=self.current_asset,
                                             texture=self.current_asset_data['import_file'])
            self.light_created.emit(light)
        elif self.current_library == "hdri":
            light = lighting_utils.create_vray_light("VRayLightDomeShape", name=self.current_asset,
                                             texture=self.current_asset_data['import_file'])
            self.light_created.emit(light)
        elif self.current_library == "gobolights":
            lighting_utils.create_gobo(self.current_asset, self.current_asset_data['import_file'])
        elif self.current_library in ['material', 'model', 'rigs', 'plants']:
            cmds.file(self.current_asset_data['import_file'], i=True)
        elif self.current_library == "texture":
            material_utils.create_texture(self.current_asset, self.current_asset_data['import_file'])

    def import_vrayproxy_action_callback(self):
        logger.info("Importing vrayproxy for %s", self.current_asset)
        logger.debug("Import file %s", self.current_asset_data['import_file'])

        cmds.file(os.path.join(libraries[self.current_library], self.current_asset, "vrayproxy",
                               "{}_vrayproxy.ma".format(self.current_asset)), i=True)

    def open_action_callback(self):
        os.startfile(self.current_asset_data['import_file'])

    def open_root_action_callback(self):
        if self.current_library in ['material', 'model', 'rigs', 'plants']:
            subprocess.Popen('explorer "{}"'.format(os.path.join(libraries[self.current_library], self.current_asset)))
        else:
            subprocess.Popen('explorer "{}"'.format(libraries[self.current_library]))

    def build_material_action_callback(self):
        logger.info("Building material: %s", self.current_asset)
        logger.debug(self.current_asset_data['material_data'])

        material_data = self.current_asset_data['material_data']

        if material_data:
            material_utils.build_material(material_data)

    def build_and_assign_material_action_callback(self):
        logger.info("Building material: %s", self.current_asset)
        logger.debug(self.current_asset_data['material_data'])

        material_data = self.current_asset_data['material_data']

        if material_data:
            selection = pm.ls(sl=1)

            material = material_utils.build_material(material_data)

            for sel in selection:
                pm.sets(material[1], edit=True, forceElement=sel)

                if material[-1]:
                    cmds.sets(str(sel), edit=True, add=str(material[-1]))

    def create_card_action_callback(self):
        logger.info("Creating card: %s", self.current_asset)

        lighting_utils.create_card(self.current_asset, self.current_asset_data['import_file'])

    def update_tags(self):
        pass
