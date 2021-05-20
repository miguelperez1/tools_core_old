from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import vray
import re

from pyqt_commons import MWidgets

from maya_core.lighting_console.constants import *
from maya_core.lighting_console import re_constants
from maya_core.lighting_console.Widgets import PropertiesWidget

reload(MWidgets)
reload(re_constants)


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
        pass

    def create_widgets(self):
        self.ls_members_header = QtWidgets.QLabel("Light Select Members")

        self.ls_members_tw = QtWidgets.QTreeWidget()
        ls_members_tw_header_item = QtWidgets.QTreeWidgetItem(['Lights'])
        self.ls_members_tw.setHeaderItem(ls_members_tw_header_item)

        self.refresh_ls_members()

        self.ls_tag_lbl = QtWidgets.QLabel("Light Select Tag")
        self.ls_tag_le = QtWidgets.QLineEdit()

        self.ls_tag_populate_btn = QtWidgets.QPushButton("Populate from tag")

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
        pass

    def refresh_ls_members(self):
        self.ls_members_tw.clear()

        ls_members = pm.sets(self.pm_node, q=True)

        for ls_member in ls_members:
            new_ls_member_item = QtWidgets.QTreeWidgetItem()
            new_ls_member_item.setText(0, str(ls_member))

            self.ls_members_tw.addTopLevelItem(new_ls_member_item)

    def refresh_attr(self):
        self.refresh_ls_members()


class AOVsWidgetProperties(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)
    renamed = QtCore.Signal(str)

    def __init__(self, node, *args, **kwargs):
        super(AOVsWidgetProperties, self).__init__(*args, **kwargs)
        self.setContentsMargins(0, 0, 0, 0)

        # self.setObjectName("ModifiersWidgetProperties")

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
                    attr_label = attr_data['label']
                    attr_widget_class = attr_data['widget_class']
                    attr_values = attr_data['values']

                    widget_class = getattr(PropertiesWidget, attr_widget_class)
                    attr_widget = widget_class(self.pm_node, attr)
                except Exception as e:
                    pass
                    print "error: " + str(e)
            else:
                pass

            if attr_widget:
                self.widgets.append(attr_widget)

        if self.class_type == "LightSelectElement":
            attr_widget = LightSelectMembersWidget(self.pm_node)
            self.widgets.append(attr_widget)

    def create_layout(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setSpacing(7)

        header_layout = QtWidgets.QHBoxLayout()
        header_layout.addWidget(self.header_lbl)
        header_layout.addWidget(self.header_le)

        self.main_layout.addLayout(header_layout)
        self.main_layout.addWidget(MWidgets.QHLine())

        # TODO Add these to a scroll area instead
        for widget in self.widgets:
            self.main_layout.addWidget(widget)

    def create_connections(self):
        self.header_le.returnPressed.connect(self.rename)

    def rename(self):
        try:
            pm.rename(self.pm_node, self.header_le.text())
        except Exception:
            pass

        self.header_le.setText(str(self.pm_node))
        self.renamed.emit(str(self.pm_node))

    def refresh_attr(self):
        for widget in self.widgets:
            widget.refresh_attr()


class AOVsWidgetItem(QtWidgets.QTreeWidgetItem):

    def __init__(self, node=None, *args, **kwargs):
        super(AOVsWidgetItem, self).__init__(*args, **kwargs)

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
        pass

    def create_widgets(self):
        self.aovs_header_lbl = MWidgets.HeaderLabel("Render Elements")

        self.aovs_create_tw = QtWidgets.QTreeWidget()
        aovs_create_header_item = QtWidgets.QTreeWidgetItem(["Create Render Element"])
        self.aovs_create_tw.setHeaderItem(aovs_create_header_item)

        self.aovs_tw = QtWidgets.QTreeWidget()
        aovs_header_item = QtWidgets.QTreeWidgetItem(["Render Elements"])
        self.aovs_tw.setHeaderItem(aovs_header_item)
        self.aovs_tw.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

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

        self.aovs_tw.currentItemChanged.connect(self.update_current_aov)

    def update_current_aov(self, item, previous_item):
        self.show_properties(item)
        if item.class_type in ["LightSelectElement"]:
            pm.select(item.text(0), noExpand=True)
        else:
            pm.select(item.text(0))

    def show_properties(self, item):
        self.push_properties.emit(item.properties_widget)

    def refresh_res(self):
        self.aovs_tw.clear()

        res = pm.ls(type='VRayRenderElement')

        res.extend(pm.ls(type="VRayRenderElementSet"))

        for re in res:
            new_aov_item = AOVsWidgetItem(re)
            self.aovs_tw.addTopLevelItem(new_aov_item)

    def create_aov(self, item, column):
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
