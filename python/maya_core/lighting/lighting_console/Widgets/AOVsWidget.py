from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import vray
import re

from pyqt_commons import MWidgets

from maya_core.lighting.lighting_console.constants import *
from maya_core.lighting.lighting_console import constants
from maya_core.lighting.lighting_console import re_constants
from maya_core.lighting.lighting_console.Widgets import PropertiesWidget


class LSMemberWidgetItem(QtWidgets.QTreeWidgetItem):

    def __init__(self, node, *args, **kwargs):
        super(LSMemberWidgetItem, self).__init__(*args, **kwargs)

        self.pm_node = node

        self.setText(0, str(self.pm_node))


class LightSelectMembersWidget(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)

    def __init__(self, node, *args, **kwargs):
        super(LightSelectMembersWidget, self).__init__(*args, **kwargs)
        self.setContentsMargins(0, 0, 0, 0)

        self.pm_node = node

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        self.add_ls_member_action = QtWidgets.QAction("Add selected lighting")
        self.remove_ls_member_action = QtWidgets.QAction("Remove Light")

    def create_widgets(self):
        self.ls_members_header = QtWidgets.QLabel("Light Select Members")

        self.ls_members_tw = QtWidgets.QTreeWidget()
        ls_members_tw_header_item = QtWidgets.QTreeWidgetItem(['Lights'])
        self.ls_members_tw.setHeaderItem(ls_members_tw_header_item)

        self.refresh_ls_members()

        self.ls_tag_lbl = QtWidgets.QLabel("Light Select Tag")
        self.ls_tag_le = QtWidgets.QLineEdit()

        self.ls_tag_populate_btn = QtWidgets.QPushButton("Populate from tag")

        self.ls_members_tw.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ls_members_tw.customContextMenuRequested.connect(self.show_ls_members_tw_context_menu)

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.addWidget(self.ls_members_header)
        main_layout.addWidget(self.ls_members_tw)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.ls_tag_lbl)
        btn_layout.addWidget(self.ls_tag_le)
        btn_layout.addStretch()
        btn_layout.addWidget(self.ls_tag_populate_btn)

        main_layout.addLayout(btn_layout)
        main_layout.addStretch()

    def create_connections(self):
        self.add_ls_member_action.triggered.connect(self.add_ls_member)
        self.remove_ls_member_action.triggered.connect(self.remove_ls_member)

    def refresh_ls_members(self):
        # log.info("AOVsWidget, LightSelectMembersWidget, refresh_ls_members")
        self.ls_members_tw.clear()

        ls_members = pm.sets(self.pm_node, q=True)

        for ls_member in ls_members:
            new_ls_member_item = LSMemberWidgetItem(ls_member)

            self.ls_members_tw.addTopLevelItem(new_ls_member_item)

    def refresh_attr(self):
        # log.info("AOVsWidget, LightSelectMembersWidget, refresh_attr")
        self.refresh_ls_members()

    def show_ls_members_tw_context_menu(self, eventPosition):
        child = self.childAt(self.sender().mapTo(self, eventPosition))
        self.current_ls_member_tw_item = self.ls_members_tw.itemAt(eventPosition)

        contextMenu = QtWidgets.QMenu(self)

        if self.current_ls_member_tw_item is not None:
            about_action = QtWidgets.QAction(str(self.current_ls_member_tw_item.pm_node))
            contextMenu.addAction(about_action)
            contextMenu.addSeparator()

            contextMenu.addAction(self.remove_ls_member_action)

        contextMenu.addAction(self.add_ls_member_action)

        action = contextMenu.exec_(child.mapToGlobal(eventPosition))

    def add_ls_member(self):
        # log.info("AOVsWidget, LightSelectMembersWidget, add_ls_member")

        for node in pm.ls(sl=1):
            if node.nodeType() != "transform":
                node = node.getTransform()

            if node.getShape().nodeType() in constants.ICONS.keys():
                if node in pm.sets(self.pm_node, q=True):
                    continue

                cmds.sets(str(node), edit=True, add=str(self.pm_node))
                new_ls_member_item = LSMemberWidgetItem(node)

                self.ls_members_tw.addTopLevelItem(new_ls_member_item)

    def remove_ls_member(self):
        # log.info("AOVsWidget, LightSelectMembersWidget, remove_ls_member")

        current_pm_node = self.current_ls_member_tw_item.pm_node

        cmds.sets(str(current_pm_node), edit=True, rm=str(self.pm_node))

        self.refresh_ls_members()


class AOVsWidgetProperties(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)
    renamed = QtCore.Signal(str)

    def __init__(self, node, *args, **kwargs):
        super(AOVsWidgetProperties, self).__init__(*args, **kwargs)
        self.setContentsMargins(0, 0, 0, 0)

        self.setMinimumSize(constants.RES_X * .95 * .125, constants.RES_Y * .875 * .575 * .9)

        self.pm_node = node
        self.class_type = self.pm_node.vrayClassType.get()

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.header_lbl = QtWidgets.QLabel("VRayRenderElement: ")
        self.header_le = QtWidgets.QLineEdit()
        self.header_le.setText(str(self.pm_node))

        self.widgets = []
        for attr in cmds.listAttr(str(self.pm_node)):
            attr_widget = None
            if attr in re_constants.VRayRenderElementsAttributes[self.class_type].keys():
                try:
                    attr_data = re_constants.VRayRenderElementsAttributes[self.class_type][attr]
                    attr_widget_class = attr_data['widget_class']

                    widget_class = getattr(PropertiesWidget, attr_widget_class)
                    attr_widget = widget_class(self.pm_node, attr_data)
                except Exception as e:
                    print str(e)
            else:
                pass

            if attr_widget:
                self.widgets.append(attr_widget)

        if self.class_type == "LightSelectElement":
            self.widgets.append(MWidgets.QHLine())

            attr_widget = LightSelectMembersWidget(self.pm_node)
            self.widgets.append(attr_widget)

    def create_layout(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setSpacing(8)

        header_layout = QtWidgets.QHBoxLayout()
        header_layout.addWidget(self.header_lbl)
        header_layout.addWidget(self.header_le)

        self.main_layout.addLayout(header_layout)
        self.main_layout.addWidget(MWidgets.QHLine())

        scroll_area_widget = QtWidgets.QScrollArea()
        scroll_area_widget.setWidgetResizable(True)
        scroll_area_widget.setFrameShape(QtWidgets.QFrame.NoFrame)

        properties_widget = QtWidgets.QWidget()
        properties_layout = QtWidgets.QVBoxLayout(properties_widget)
        properties_layout.setContentsMargins(0, 0, 0, 0)
        properties_layout.setSpacing(8)

        for widget in self.widgets:
            properties_layout.addWidget(widget)

        properties_layout.addStretch()

        scroll_area_widget.setWidget(properties_widget)

        self.main_layout.addWidget(scroll_area_widget)

    def create_connections(self):
        self.header_le.returnPressed.connect(self.rename)

    def rename(self):
        # log.info("AOVsWidget, AOVsWidgetProperties, rename")

        try:
            pm.rename(self.pm_node, self.header_le.text())
        except Exception:
            pass

        self.header_le.setText(str(self.pm_node))
        self.renamed.emit(str(self.pm_node))

    def refresh_attr(self):
        # log.info("AOVsWidget, AOVsWidgetProperties, refresh_attr")

        for widget in self.widgets:
            if hasattr(widget, 'refresh_attr'):
                widget.refresh_attr()


class AOVsWidgetItem(QtWidgets.QTreeWidgetItem):

    def __init__(self, node=None, *args, **kwargs):
        super(AOVsWidgetItem, self).__init__(*args, **kwargs)
        self.setFlags(self.flags() | QtCore.Qt.ItemIsEditable)

        self.pm_node = node

        self.class_type = self.pm_node.vrayClassType.get()

        self.setText(0, str(self.pm_node))

        self.properties_widget = AOVsWidgetProperties(self.pm_node)

        self.properties_widget.renamed.connect(self.rename)

    def rename(self, new_name):
        self.setText(0, new_name)


class AOVsWidget(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)
    push_properties = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        super(AOVsWidget, self).__init__(*args, **kwargs)

        self.setObjectName("AOVsWidget")

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.setContentsMargins(0, 0, 0, 0)

        self.refresh_res()

    def create_actions(self):
        self.remove_aov_action = QtWidgets.QAction("Remove")
        self.duplicate_aov_action = QtWidgets.QAction("Duplicate")

    def create_widgets(self):
        self.aovs_header_lbl = MWidgets.HeaderLabel("Render Elements")

        self.aovs_create_tw = QtWidgets.QTreeWidget()
        aovs_create_header_item = QtWidgets.QTreeWidgetItem(["Create Render Element"])
        self.aovs_create_tw.setHeaderItem(aovs_create_header_item)

        self.aovs_tw = MWidgets.MTreeWidget()
        aovs_header_item = QtWidgets.QTreeWidgetItem(["Render Elements"])
        self.aovs_tw.setHeaderItem(aovs_header_item)
        self.aovs_tw.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.aovs_tw.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.aovs_tw.customContextMenuRequested.connect(self.show_aovs_tw_context_menu)

        for aov in re_constants.VRayAOVS.keys():
            item = QtWidgets.QTreeWidgetItem()
            item.setText(0, aov)
            self.aovs_create_tw.addTopLevelItem(item)

        self.re_remove_btn = QtWidgets.QPushButton("-")
        self.re_remove_btn.setFixedSize(30, 30)

        self.re_refresh_btn = MWidgets.ImagePushButton(30, 30)
        self.re_refresh_btn.set_image("F:\\share\\tools\\shelf_icons\\refresh.png")
        self.re_refresh_btn.setFixedSize(30, 30)

        self.re_duplicate_btn = MWidgets.ImagePushButton(30, 30)
        self.re_duplicate_btn.set_image("F:\\share\\tools\\shelf_icons\\duplicate.png")
        self.re_duplicate_btn.setFixedSize(30, 30)

    def create_layout(self):
        aovs_layout = QtWidgets.QVBoxLayout(self)
        aovs_layout.setSpacing(GLOBAL_SPACING)

        aovs_header_layout = QtWidgets.QHBoxLayout()
        aovs_header_layout.setSpacing(GLOBAL_SPACING)

        aovs_header_layout.addWidget(self.aovs_header_lbl)

        aovs_btns_layout = QtWidgets.QHBoxLayout()
        aovs_btns_layout.setSpacing(GLOBAL_SPACING)

        aovs_btns_layout.addStretch()
        aovs_btns_layout.addWidget(self.re_refresh_btn)
        aovs_btns_layout.addWidget(self.re_remove_btn)
        aovs_btns_layout.addWidget(self.re_duplicate_btn)

        aovs_header_layout.addLayout(aovs_btns_layout)

        aovs_layout.addLayout(aovs_header_layout)

        aovs_tw_layout = QtWidgets.QHBoxLayout()
        aovs_tw_layout.setSpacing(GLOBAL_SPACING)

        aovs_tw_layout.addWidget(self.aovs_create_tw)
        aovs_tw_layout.addWidget(self.aovs_tw)

        aovs_layout.addLayout(aovs_tw_layout)

    def create_connections(self):
        self.aovs_create_tw.itemDoubleClicked.connect(self.create_aov)

        self.aovs_tw.itemSelectionChanged.connect(self.update_current_aov)
        self.aovs_tw.itemChanged.connect(self.rename_aov)

        self.remove_aov_action.triggered.connect(self.remove_aov)
        self.duplicate_aov_action.triggered.connect(self.duplicate_aov)

    def rename_aov(self, item, column):
        # log.info("AOVsWidget, AOVsWidget, rename_aov")

        try:
            pm.rename(item.pm_node, item.text(0))
            self.refresh_res()
        except Exception:
            pass

    def remove_aov(self):
        # log.info("AOVsWidget, AOVsWidget, remove_aov")

        try:
            pm.delete(self.current_aov_tw_item.pm_node)
            self.refresh_res()
        except Exception:
            pass

    def duplicate_aov(self):
        # log.info("AOVsWidget, AOVsWidget, duplicate_aov")

        try:
            pm.duplicate(self.current_aov_tw_item.pm_node, un=True)
            self.refresh_res()
        except Exception:
            pass

    def update_current_aov(self):
        # log.info("AOVsWidget, AOVsWidget, update_current_aov")

        if not self.aovs_tw.selectedItems():
            self.push_properties.emit(None)
            return

        item = self.aovs_tw.selectedItems()[0]

        if item is not None:
            self.show_properties(item)
            if item.class_type in ["LightSelectElement"]:
                pm.select(item.text(0), noExpand=True)
            else:
                pm.select(item.text(0))

    def show_properties(self, item):
        # log.info("AOVsWidget, AOVsWidget, show_properties")

        if item is not None:
            self.push_properties.emit(item.properties_widget)
        else:
            self.push_properties.emit(None)

    def refresh_res(self):
        # log.info("AOVsWidget, AOVsWidget, refresh_res")

        self.aovs_tw.blockSignals(True)

        self.aovs_tw.clear()

        res = pm.ls(type='VRayRenderElement')

        res.extend(pm.ls(type="VRayRenderElementSet"))

        for re in res:
            new_aov_item = AOVsWidgetItem(re)
            self.aovs_tw.addTopLevelItem(new_aov_item)

        self.aovs_tw.blockSignals(False)

        self.push_properties.emit(None)

    def create_aov(self, item, column):
        # log.info("AOVsWidget, AOVsWidget, create_aov")

        command = re_constants.VRayAOVS[item.text(0)]
        pm_node = pm.PyNode(mel.eval("vrayAddRenderElement {}".format(command)))

        try:
            pm.rename(pm_node, str(pm_node).replace("vrayRE_", ""))
        except Exception:
            pass

        new_aov_item = AOVsWidgetItem(pm_node)

        self.aovs_tw.addTopLevelItem(new_aov_item)

        self.aovs_tw.clearSelection()
        self.aovs_tw.setItemSelected(new_aov_item, True)
        self.push_properties.emit(new_aov_item.properties_widget)

    def show_aovs_tw_context_menu(self, eventPosition):
        child = self.childAt(self.sender().mapTo(self, eventPosition))
        self.current_aov_tw_item = self.aovs_tw.itemAt(eventPosition)

        contextMenu = QtWidgets.QMenu(self)

        if self.current_aov_tw_item is not None:
            about_action = QtWidgets.QAction(str(self.current_aov_tw_item.pm_node))
            contextMenu.addAction(about_action)
            contextMenu.addSeparator()

            contextMenu.addAction(self.remove_aov_action)
            contextMenu.addAction(self.duplicate_aov_action)

        action = contextMenu.exec_(child.mapToGlobal(eventPosition))
