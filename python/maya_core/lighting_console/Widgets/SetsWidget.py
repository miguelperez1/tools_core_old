from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import pymel.core as pm
import vray

from pyqt_commons import MWidgets

reload(MWidgets)

from maya_core.lighting_console.constants import *


# TODO Sets created script job
# TODO Select Set

class SetsWidgetItem(QtWidgets.QTreeWidgetItem):
    log_event = QtCore.Signal(str, str)

    def __init__(self, set, *args, **kwargs):
        super(SetsWidgetItem, self).__init__(*args, **kwargs)

        self.pm_node = pm.PyNode(set)
        self.setText(0, set)
        self.setFlags(self.flags() | QtCore.Qt.ItemIsEditable)


class SetsWidget(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)

    def __init__(self, *args, **kwargs):
        super(SetsWidget, self).__init__(*args, **kwargs)

        self.setObjectName("SetsWidget")

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.setContentsMargins(0, 0, 0, 0)

    def create_actions(self):
        self.add_set_action = QtWidgets.QAction("Add Set")
        self.remove_set_action = QtWidgets.QAction("Remove Set")
        self.duplicate_set_action = QtWidgets.QAction("Duplicate Set")
        self.add_to_set_action = QtWidgets.QAction("Add selected to set")
        self.remove_from_set_action = QtWidgets.QAction("Remove from set")
        self.refresh_sets_action = QtWidgets.QAction("Refresh Sets")

    def create_widgets(self):
        self.sets_header_lbl = MWidgets.HeaderLabel("Sets")
        self.sets_tw = QtWidgets.QTreeWidget()
        sets_tw_header_item = QtWidgets.QTreeWidgetItem(['Sets'])
        self.sets_tw.setHeaderItem(sets_tw_header_item)

        self.set_members_tw = QtWidgets.QTreeWidget()
        set_members_tw_header_item = QtWidgets.QTreeWidgetItem(['Set Members'])
        self.set_members_tw.setHeaderItem(set_members_tw_header_item)

        self.add_set_btn = QtWidgets.QPushButton("+")
        self.add_set_btn.setFixedSize(30, 30)

        self.remove_set_btn = QtWidgets.QPushButton("-")
        self.remove_set_btn.setFixedSize(30, 30)

        self.sets_refresh_btn = MWidgets.ImagePushButton(30, 30)
        self.sets_refresh_btn.set_image("F:\\share\\tools\\shelf_icons\\refresh.png")
        self.sets_refresh_btn.setFixedSize(30, 30)

        self.sets_duplicate_btn = MWidgets.ImagePushButton(30, 30)
        self.sets_duplicate_btn.set_image("F:\\share\\tools\\shelf_icons\\duplicate.png")
        self.sets_duplicate_btn.setFixedSize(30, 30)

        self.sets_tw.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.sets_tw.customContextMenuRequested.connect(self.show_sets_tw_context_menu)

        self.set_members_tw.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.set_members_tw.customContextMenuRequested.connect(self.show_set_members_tw_context_menu)

        self.update_sets()

    def create_layout(self):
        sets_layout = QtWidgets.QVBoxLayout(self)
        sets_layout.setSpacing(GLOBAL_SPACING)

        sets_btn_layout = QtWidgets.QHBoxLayout()
        sets_btn_layout.setSpacing(GLOBAL_SPACING)

        sets_btn_layout.addWidget(self.sets_header_lbl)
        sets_btn_layout.addStretch()
        sets_btn_layout.addWidget(self.sets_refresh_btn)
        sets_btn_layout.addWidget(self.add_set_btn)
        sets_btn_layout.addWidget(self.remove_set_btn)
        sets_btn_layout.addWidget(self.sets_duplicate_btn)

        sets_layout.addLayout(sets_btn_layout)

        sets_tw_layout = QtWidgets.QHBoxLayout()
        sets_tw_layout.setSpacing(GLOBAL_SPACING)
        sets_tw_layout.addWidget(self.sets_tw)
        sets_tw_layout.addWidget(self.set_members_tw)

        sets_layout.addLayout(sets_tw_layout)

    def create_connections(self):
        self.add_set_btn.clicked.connect(self.add_set)
        self.remove_set_btn.clicked.connect(self.remove_set)

        self.add_set_action.triggered.connect(self.add_set)
        self.remove_set_action.triggered.connect(self.remove_set)
        self.duplicate_set_action.triggered.connect(self.duplicate_set)
        self.add_to_set_action.triggered.connect(self.add_to_set)
        self.remove_from_set_action.triggered.connect(self.remove_from_set)
        self.refresh_sets_action.triggered.connect(self.update_sets)

        self.sets_tw.currentItemChanged.connect(self.update_current_set)
        self.sets_tw.itemChanged.connect(self.sets_tw_rename_callback)

        self.sets_refresh_btn.clicked.connect(self.update_sets)
        self.sets_duplicate_btn.clicked.connect(self.duplicate_set)

    def show_sets_tw_context_menu(self, eventPosition):
        child = self.childAt(self.sender().mapTo(self, eventPosition))
        self.current_set_item = self.sets_tw.itemAt(eventPosition)

        contextMenu = QtWidgets.QMenu(self)

        if self.current_set is None:
            contextMenu.addAction(self.add_set_action)
            contextMenu.addAction(self.refresh_sets_action)

        else:
            about_action = QtWidgets.QAction(self.current_set)
            about_action.triggered.connect(self.select_set)

            contextMenu.addAction(about_action)
            contextMenu.addSeparator()
            contextMenu.addAction(self.add_set_action)
            contextMenu.addAction(self.remove_set_action)
            contextMenu.addAction(self.duplicate_set_action)
            contextMenu.addSeparator()
            contextMenu.addAction(self.refresh_sets_action)

        action = contextMenu.exec_(child.mapToGlobal(eventPosition))

    def select_set(self):
        pm.select(self.current_set_item.pm_node, noExpand=True)

    def show_set_members_tw_context_menu(self, eventPosition):
        child = self.childAt(self.sender().mapTo(self, eventPosition))
        self.current_set_member_item = self.set_members_tw.itemAt(eventPosition)

        contextMenu = QtWidgets.QMenu(self)

        if self.current_set_member_item is not None:
            about_action = QtWidgets.QAction(self.current_set_member_item.text(0))
            contextMenu.addAction(about_action)
            contextMenu.addSeparator()
            contextMenu.addAction(self.remove_from_set_action)
            contextMenu.addSeparator()

        contextMenu.addAction(self.add_to_set_action)
        contextMenu.addAction(self.refresh_sets_action)

        action = contextMenu.exec_(child.mapToGlobal(eventPosition))

    def update_current_set(self, current_item=None):
        self.current_set_item = current_item

        if current_item is not None:
            self.current_set = self.current_set_item.text(0)
        else:
            self.current_set = None

        self.update_set_members()

    def sets_tw_rename_callback(self, item, column):
        prev_set_name = self.current_set
        new_set_name = item.text(0)

        cmds.rename(self.current_set, new_set_name)

        self.update_current_set(item)

    def update_sets(self):
        self.sets_tw.clear()
        self.update_current_set()

        sets = []
        for objectset in cmds.ls(type="objectSet"):
            if cmds.nodeType(objectset) != "objectSet":
                continue
            sets.append(objectset)

        for set in sets:
            if set.startswith("default") or set.startswith("initial"):
                continue

            item = SetsWidgetItem(set)
            self.sets_tw.addTopLevelItem(item)

        self.update_set_members()

    def update_set_members(self):
        self.set_members_tw.clear()

        if self.current_set is None:
            return

        members = cmds.sets(self.current_set, q=True)

        if members is None:
            return

        for m in members:
            item = QtWidgets.QTreeWidgetItem()
            item.setText(0, str(m))
            self.set_members_tw.addTopLevelItem(item)

    def add_set(self):
        new_set = cmds.sets(empty=True)

        self.log_event.emit("result", ("Created " + new_set))

        self.update_sets()

    def remove_set(self):
        if self.current_set is None:
            return

        cmds.delete(self.current_set)

        self.log_event.emit("result", ("Deleted " + self.current_set))

        self.update_sets()

    def add_to_set(self):
        for obj in cmds.ls(sl=True):
            cmds.sets(obj, edit=True, add=self.current_set)

        if len(cmds.ls(sl=True)) > 1:
            self.log_event.emit("result", "Added objects to {0}".format(self.current_set))
        elif len(cmds.ls(sl=True)) == 1:
            self.log_event.emit("result", "Added {0} to {1}".format(cmds.ls(sl=True)[0]), self.current_set)

        self.update_set_members()

    def remove_from_set(self):
        for obj in cmds.ls(sl=True):
            cmds.sets(obj, edit=True, rm=self.current_set)

        if len(cmds.ls(sl=True)) > 1:
            self.log_event.emit("result", "Removed objects from {0}".format(self.current_set))
        elif len(cmds.ls(sl=True)) == 1:
            self.log_event.emit("result", "Removed {0} from {1}".format(cmds.ls(sl=True)[0]), self.current_set)

        self.update_set_members()

    def duplicate_set(self):
        if self.current_set is None:
            return

        current_set = self.current_set

        new_set = cmds.duplicate(self.current_set)[0]

        try:
            for obj in cmds.sets(self.current_set, q=True):
                cmds.sets(obj, edit=True, add=new_set)
        except TypeError:
            pass

        self.update_sets()

        for i in range(self.sets_tw.topLevelItemCount()):
            if self.sets_tw.topLevelItem(i).text(0) == new_set:
                self.update_current_set(self.sets_tw.topLevelItem(i))

                self.update_set_members()

                self.sets_tw.topLevelItem(i).setSelected(True)

        self.log_event.emit("result", ("Duplicated {0} to {1}".format(current_set, new_set)))
