from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

from shutil import copyfile

import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel

from maya_core.common_tools import yaml_reader
from maya_core import asset_manager

import os
import sys
import subprocess
import operator
from collections import OrderedDict, defaultdict
import imagesize

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


class OrderedDefaultDict(OrderedDict, defaultdict):
    def __init__(self, default_factory=None, *args, **kwargs):
        super(OrderedDefaultDict, self).__init__(*args, **kwargs)
        self.default_factory = default_factory


class PreviewLabel(QtWidgets.QLabel):
    def __init__(self, *args, **kwargs):
        super(PreviewLabel, self).__init__(*args, **kwargs)
        self.set_default()
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setMinimumSize(1, 1)
        self.setContentsMargins(5, 5, 5, 5)
        self.setText('Test')

    def set_image(self, path, scale=160 * 1.3):
        self.pixmap = QtGui.QPixmap(path).scaledToWidth(scale, QtCore.Qt.SmoothTransformation)
        self.setPixmap(self.pixmap)

    def set_default(self):
        self.setPixmap(
            QtGui.QPixmap(r'F:\share\tools\core\maya_core\asset_browser\icons\default.png').scaledToWidth(100,
                                                                                                          QtCore.Qt.SmoothTransformation))


def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class AssetBrowser(QtWidgets.QDialog):
    """
    Dialog used to demonstrates many of the standard dialogs available in Qt
    """

    def __init__(self, parent=maya_main_window()):
        super(AssetBrowser, self).__init__(parent)

        self.setWindowTitle("Asset Browser")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.setFixedSize(940 * 1.25, 890 * 1.25)

        self.setWindowFlags(
            self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

        self.library = self.tab_widget.tabText(self.tab_widget.currentIndex()).lower()
        self.update_asset_count()

    def create_actions(self):
        # Default Actions
        self.open_action = QtWidgets.QAction("Open", self)
        self.open_root_action = QtWidgets.QAction("Open in Explorer", self)
        self.open_preview_action = QtWidgets.QAction("Open Preview", self)
        self.replace_preview_action = QtWidgets.QAction('Replace Preview', self)

        # Common Actions
        self.import_action = QtWidgets.QAction("Import", self)
        self.reference_action = QtWidgets.QAction("Reference", self)

        # Material Actions
        self.material_import_assign_action = QtWidgets.QAction('Import and assign to selected', self)

    def create_widgets(self):
        # Create Asset Preview Widgets
        self.asset_widgets = OrderedDefaultDict(list)

        for library, library_path in LIBRARIES.items():
            library_yml = library_path + "\\library.yml"

            data = yaml_reader.read_yaml(library_yml)
            library_data = sorted(data.items(), key=operator.itemgetter(0))

            for asset_data in library_data:
                asset = asset_data[0]
                preview_path = asset_data[1]

                widget = PreviewLabel()
                widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
                widget.customContextMenuRequested.connect(self.show_context_menu)
                widget.setAccessibleName(asset)
                widget.setToolTip(widget.accessibleName())
                widget.setObjectName(preview_path)

                if os.path.isfile(preview_path):
                    widget.set_image(preview_path)
                else:
                    widget.set_default()

                widget_data = (asset, widget)

                self.asset_widgets[library].append(widget_data)

        self.asset_count_lbl = QtWidgets.QLabel("Asset Count: ")

    def create_layout(self):
        self.tab_widget = QtWidgets.QTabWidget()

        for library, library_widgets in self.asset_widgets.items():
            sorted_widgets = sorted(library_widgets, key=lambda x: x[0].lower())

            library_widget = QtWidgets.QWidget()

            library_layout = QtWidgets.QGridLayout(library_widget)

            library_layout.setContentsMargins(5, 5, 5, 5)

            row = 0
            column = 0
            for widget_data in sorted_widgets:
                if column == 5:
                    row = row + 1
                    column = 0
                library_layout.addWidget(widget_data[1], row, column, 1, 1)
                column = column + 1

            library_scroll_area = QtWidgets.QScrollArea()
            library_scroll_area.setWidgetResizable(False)
            library_scroll_area.setStyleSheet('border: none;')
            library_scroll_area.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
            library_scroll_area.setWidget(library_widget)

            self.tab_widget.addTab(library_scroll_area, library.capitalize())

        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.addWidget(self.tab_widget)
        main_layout.addWidget(self.asset_count_lbl)

    def create_connections(self):
        # Default Actions
        self.open_action.triggered.connect(self.open_action_callback)
        self.open_root_action.triggered.connect(self.open_root_action_callback)
        self.replace_preview_action.triggered.connect(self.replace_preview_action_callback)
        self.open_preview_action.triggered.connect(self.open_preview_action_callback)

        # Common Actions
        self.import_action.triggered.connect(self.import_action_callback)
        self.reference_action.triggered.connect(self.reference_action_callback)

        # Material Actions
        self.material_import_assign_action.triggered.connect(self.material_import_assign_action_callback)

        self.tab_widget.currentChanged.connect(self.tab_widget_callback)

    def tab_widget_callback(self):
        self.library = self.tab_widget.tabText(self.tab_widget.currentIndex()).lower()
        self.update_asset_count()

    def update_asset_count(self):
        count = self.tab_widget.currentWidget().widget().layout().count()
        self.asset_count_lbl.setText("Asset Count: {}".format(count))

    def show_context_menu(self, eventPosition):
        child = self.childAt(self.sender().mapTo(self, eventPosition))

        self.current_asset = child.accessibleName()
        self.current_preview_path = child.objectName()

        contextMenu = QtWidgets.QMenu(self)

        self.about_action = QtWidgets.QAction(self.current_asset)
        contextMenu.addAction(self.about_action)

        contextMenu.addSeparator()

        contextMenu.addAction(self.open_action)
        contextMenu.addAction(self.replace_preview_action)
        contextMenu.addAction(self.open_preview_action)
        contextMenu.addAction(self.open_root_action)

        contextMenu.addSeparator()

        contextMenu.addAction(self.import_action)

        if self.library in NORMAL_LIBRARIES:
            contextMenu.addAction(self.reference_action)

        contextMenu.addSeparator()

        if self.library == "material":
            contextMenu.addAction(self.material_import_assign_action)

        action = contextMenu.exec_(child.mapToGlobal(eventPosition))

    def open_action_callback(self):
        library_path = LIBRARIES_ROOT + "" + self.library
        maya_path = library_path + "\\{0}_root\\maya\\{0}.ma".format(self.current_asset)
        os.startfile(maya_path)

    def open_root_action_callback(self):
        library_path = LIBRARIES_ROOT + "\\" + self.library
        if self.library in NORMAL_LIBRARIES:
            root_path = os.path.join(library_path.replace("\\\\", "\\"), "{0}_root".format(self.current_asset))
        else:
            root_path = LIBRARIES[self.library]

        subprocess.Popen('explorer "{}"'.format(root_path))

    def replace_preview_action_callback(self):
        dst = self.current_preview_path
        src = QtWidgets.QFileDialog.getOpenFileName(self, 'Select New Preview Image')[0]

        copyfile(src, dst)

    def open_preview_action_callback(self):
        os.system("start " + self.current_preview_path)

    def import_action_callback(self):
        if self.library in NORMAL_LIBRARIES:
            library_path = LIBRARIES_ROOT + "\\" + self.library
            tmp_path = library_path + "\\{0}_root\\maya\\{0}.ma".format(self.current_asset)

            if os.path.isfile(tmp_path):
                maya_path = tmp_path
            elif os.path.isfile(tmp_path.replace('.ma', '.mb')):
                maya_path = tmp_path.replace('.ma', '.mb')

            cmds.file(maya_path, i=True)

        elif self.library == "studio_lights":
            self.import_studio_light()
        elif self.library == "hdri":
            self.import_hdr()
        elif self.library == "clouds":
            self.import_cloud()

    def reference_action_callback(self):
        if self.library in NORMAL_LIBRARIES:
            library_path = LIBRARIES_ROOT + "\\" + self.library
            tmp_path = library_path + "\\{0}_root\\maya\\{0}.ma".format(self.current_asset)

            if os.path.isfile(tmp_path):
                maya_path = tmp_path
            elif os.path.isfile(tmp_path.replace('.ma', '.mb')):
                maya_path = tmp_path.replace('.ma', '.mb')

            cmds.file(maya_path, reference=True)

    def material_import_assign_action_callback(self):
        library_path = LIBRARIES_ROOT + "\\" + self.library
        maya_path = library_path + "\\{0}_root\\maya\\{0}.ma".format(self.current_asset)

        shading_group = self.current_asset + "_mat_shading_group"

        selected = cmds.ls(sl=True)

        cmds.file(maya_path, i=True)

        for node in selected:
            cmds.sets(node, e=True, forceElement=shading_group)

    def import_cloud(self):
        cloud_path = LIBRARIES['clouds'] + "\\{}.vdb".format(self.current_asset)
        cloud_node_vray = cmds.createNode('VRayVolumeGrid', n='{}_vray_volume_grid'.format(self.current_asset))
        cmds.rename('transform1', '{}'.format(self.current_asset))
        cloud_node = '{}'.format(self.current_asset)

        cmds.setAttr('{}.inPath'.format(cloud_node), cloud_path, type="string")
        cmds.setAttr('{}.gpuViewEnbl'.format(cloud_node), 1)
        cmds.setAttr('{}.viewAutoReduction'.format(cloud_node), 0)
        cmds.setAttr('{}.volZDepth'.format(cloud_node_vray), 1)
        cmds.setAttr('{}.detailReduction'.format(cloud_node), 2)

    def import_hdr(self):
        path = LIBRARIES['hdri'] + '\\{}'.format(self.current_asset)

        dome_trans = cmds.createNode('transform', n='{}_vray_dome_light'.format(self.current_asset[:-4]))
        dome_light = cmds.createNode('VRayLightDomeShape', n='{}_vray_dome_lightShape'.format(self.current_asset[:-4]),
                                     p=dome_trans)
        mel.eval('sets -edit -forceElement  defaultLightSet {} ;'.format(dome_light))

        cmds.setAttr('{}.useDomeTex'.format(dome_light), 1)
        cmds.setAttr('{}.invisible'.format(dome_light), 1)
        cmds.setAttr('{}.viewportTexEnable'.format(dome_light), 0)

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
        cmds.connectAttr('{}.outColor'.format(cc_node), '{}.domeTex'.format(dome_light))

    def import_studio_light(self):
        path = LIBRARIES['studio_lights'] + '\\{}'.format(self.current_asset)
        area_trans = cmds.createNode('transform', n='{}_vray_rect_light'.format(self.current_asset[:-4]))
        area_lgt = cmds.createNode('VRayLightRectShape', n='{}_vray_rect_lightShape'.format(self.current_asset[:-4]),
                                   p=area_trans)
        cmds.setAttr('{}.useRectTex'.format(area_lgt), 1)
        mel.eval('sets -edit -forceElement defaultLightSet {} ;'.format(area_lgt))
        tex = cmds.shadingNode('file', asTexture=True, isColorManaged=True)
        cmds.connectAttr('{}.outColor'.format(tex), '{}.rectTex'.format(area_lgt))
        cmds.setAttr('{}.fileTextureName'.format(tex), path, type='string')
        cmds.setAttr('{}.intensityMult'.format(area_lgt), 1)
        cmds.setAttr('{}.showTex'.format(area_lgt), 1)
        cmds.setAttr('{}.invisible'.format(area_lgt), 1)
        cmds.setAttr('{}.multiplyByTheLightColor'.format(area_lgt), 1)

        aspect_ratio = self.get_preview_size()

        cmds.setAttr('{}.scaleY'.format(area_trans), 1 / aspect_ratio)

    def get_preview_size(self):
        asset_image_path = self.current_preview_path
        image_size = imagesize.get(asset_image_path)
        aspect_ratio = float(float(image_size[0]) / float(image_size[1]))

        return aspect_ratio


def main():
    try:
        asset_browser.close()
        asset_browser.deleteLater()
    except:
        pass

    asset_browser = AssetBrowser()
    asset_browser.show()


if __name__ == "__main__":
    main()
