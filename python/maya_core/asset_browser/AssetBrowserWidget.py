import os
import re
from collections import OrderedDict

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds

from pyqt_commons import MWidgets
from maya_core.asset_manager.library_utils import library_utils
from maya_core.asset_manager.library_utils import constants
from maya_core.lighting.lighting_utils import lighting_utils

reload(library_utils)
reload(lighting_utils)

LIBRARIES = constants.libraries


class AssetBrowserWidget(QtWidgets.QWidget):
    def __init__(self, width, height, use_tags_widget=1):
        super(AssetBrowserWidget, self).__init__()
        self.setObjectName("AssetBrowserUI")
        self.size = (width, height)
        self.use_tags_widget = use_tags_widget

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
        self.open_preview_action = QtWidgets.QAction("Open Preview", self)
        self.replace_preview_action = QtWidgets.QAction('Replace Preview', self)

        # Common Actions
        self.import_action = QtWidgets.QAction("Import", self)
        self.reference_action = QtWidgets.QAction("Reference", self)
        self.import_proxy_action = QtWidgets.QAction("Import VRay Proxy", self)

        # Material Actions
        self.material_import_assign_action = QtWidgets.QAction('Import and assign to selected', self)

    def create_widgets(self):
        self.search_lble = MWidgets.LabeledLineEdit('Search')

        self.libraries_tw = QtWidgets.QTreeWidget()
        header_item = QtWidgets.QTreeWidgetItem()
        header_item.setText(0, 'Libraries')
        self.libraries_tw.setHeaderItem(header_item)
        self.libraries_tw.setAlternatingRowColors(True)
        self.libraries_tw.setMaximumWidth(self.width() * .2)

        for library in sorted(LIBRARIES.keys()):
            if library == 'root':
                continue

            library_item = QtWidgets.QTreeWidgetItem()
            library_item.setText(0, library.title())

            library_data = library_utils.get_library_data(library)

            for tag in library_data["tags"]:
                if not tag:
                    continue

                tag_item = QtWidgets.QTreeWidgetItem()
                tag_item.setText(0, tag.title())

                library_item.addChild(tag_item)

            self.libraries_tw.addTopLevelItem(library_item)

        self.assets_tw = QtWidgets.QTreeWidget()
        header_item = QtWidgets.QTreeWidgetItem(['Preview', 'Asset'])
        self.assets_tw.setHeaderItem(header_item)
        self.assets_tw.setMinimumWidth(self.width() * .8)
        self.assets_tw.setColumnWidth(0, 200)
        self.assets_tw.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.create_asset_item_widgets()

    def create_asset_item_widgets(self):
        self.asset_item_widgets = []
        for library in LIBRARIES.keys():
            library_data = library_utils.get_library_data(library)

            if not library_data:
                continue

            for asset_data in library_data["assets"]:
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

                asset_item = QtWidgets.QTreeWidgetItem()
                asset_item.setText(1, asset)
                asset_item.setData(0, QtCore.Qt.UserRole, new_asset_data)

                self.assets_tw.addTopLevelItem(asset_item)
                self.assets_tw.setItemWidget(asset_item, 0, preview_widget)
                asset_item.setHidden(True)

                self.asset_item_widgets.append(asset_item)

    def refresh_asset_items(self):
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

        self.import_action.triggered.connect(self.import_action_callback)

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

        contextMenu.addAction(self.import_action)

        if self.current_library in ['model', 'material', 'rigs', 'plants']:
            contextMenu.addAction(self.reference_action)

            asset_path = os.path.join(library_utils.libraries[self.current_library], asset)

            if "vrayproxy" in os.listdir(asset_path):
                contextMenu.addAction(self.import_proxy_action)

        contextMenu.addSeparator()

        if self.current_library == "material":
            contextMenu.addAction(self.material_import_assign_action)

        contextMenu.addSeparator()

        contextMenu.addAction(self.open_action)
        contextMenu.addAction(self.replace_preview_action)
        contextMenu.addAction(self.open_preview_action)
        contextMenu.addAction(self.open_root_action)

        action = contextMenu.exec_(self.assets_tw.mapToGlobal(eventPosition))

    def import_action_callback(self):
        if self.current_library == "studiolights":
            lighting_utils.create_vray_light("VRayLightRectShape", name=self.current_asset,
                                             texture=self.current_asset_data['import_file'])
        elif self.current_library == "hdri":
            lighting_utils.create_vray_light("VRayLightDomeShape", name=self.current_asset,
                                             texture=self.current_asset_data['import_file'])
        elif self.current_library == "gobolights":
            lighting_utils.create_gobo(self.current_asset, self.current_asset_data['import_file'])
        elif self.current_library in ['material', 'model', 'rigs', 'plants']:
            cmds.file(self.current_asset_data['import_file'], i=True)
