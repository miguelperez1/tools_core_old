from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import pymel.core as pm

from pyqt_commons import MWidgets
from maya_core.modeling.mash_builder import mash_builder

reload(MWidgets)
reload(mash_builder)


class MASHBuilderUI(QtWidgets.QMainWindow):
    def __init__(self, parent=MWidgets.maya_main_window()):
        super(MASHBuilderUI, self).__init__(parent)

        self.setWindowTitle("MASH Builder")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.setObjectName("MASHBuilderUI")

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.setMinimumSize(800, 400)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        self.add_object_action = QtWidgets.QAction("Add selected object")
        self.remove_object_action = QtWidgets.QAction("Remove object")

    def create_widgets(self):
        self.network_name_lble = MWidgets.LabeledLineEdit("Network Name: ")

        self.scatter_amount = MWidgets.LabeledIntSlider("Number of Points: ", 0, 7000, 0)

        self.geo_type_lbl = QtWidgets.QLabel("Geometry Type: ")
        self.geo_type_cmbx = QtWidgets.QComboBox()
        self.geo_type_cmbx.addItems(["Mesh", "Instancer"])
        self.geo_type_cmbx.setCurrentText("Instancer")

        self.distribute_type_lbl = QtWidgets.QLabel("Distribute Type: ")

        self.distribute_type_cmbx = QtWidgets.QComboBox()
        self.distribute_type_cmbx.addItems(["Linear", "Mesh", "Grid"])

        self.mesh_input_lble = MWidgets.LabeledLineEdit("Mesh: ")

        self.add_random_cb = QtWidgets.QCheckBox("Add Default Random")

        self.objects_tw = QtWidgets.QTreeWidget()
        header_item = QtWidgets.QTreeWidgetItem(["Objects"])
        self.objects_tw.setHeaderItem(header_item)

        self.objects_tw.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.objects_tw.customContextMenuRequested.connect(self.show_objects_tw_context_menu)
        self.current_object_item = None

        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.build_btn = QtWidgets.QPushButton("Build")

        self.distribute_type_cmbx_callback()

    def create_layout(self):
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)

        row_1_layout = QtWidgets.QHBoxLayout()
        row_1_layout.addWidget(self.network_name_lble)
        row_1_layout.addWidget(self.geo_type_lbl)
        row_1_layout.addWidget(self.geo_type_cmbx)
        row_1_layout.addWidget(self.distribute_type_lbl)
        row_1_layout.addWidget(self.distribute_type_cmbx)

        main_layout.addLayout(row_1_layout)
        main_layout.addWidget(self.mesh_input_lble)
        main_layout.addWidget(self.scatter_amount)
        main_layout.addWidget(self.objects_tw)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.add_random_cb)
        btn_layout.addStretch()
        btn_layout.addWidget(self.build_btn)
        btn_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(btn_layout)

    def create_connections(self):
        self.distribute_type_cmbx.currentIndexChanged.connect(self.distribute_type_cmbx_callback)
        self.add_object_action.triggered.connect(self.add_object_action_callback)
        self.remove_object_action.triggered.connect(self.remove_object_action_callback)
        self.build_btn.clicked.connect(self.build_btn_callback)
        self.cancel_btn.clicked.connect(self.close)

    def add_object_action_callback(self):
        for obj in pm.ls(sl=1):
            item = QtWidgets.QTreeWidgetItem()
            item.setText(0, str(obj))
            self.objects_tw.addTopLevelItem(item)

    def remove_object_action_callback(self):
        if self.current_object_item:
            index = self.objects_tw.indexFromItem(self.current_object_item).row()

            self.objects_tw.takeTopLevelItem(index)

    def distribute_type_cmbx_callback(self):
        if self.distribute_type_cmbx.currentText() == "Mesh":
            self.mesh_input_lble.setHidden(False)
        else:
            self.mesh_input_lble.setHidden(True)

    def show_objects_tw_context_menu(self, eventPosition):
        child = self.childAt(self.sender().mapTo(self, eventPosition))
        self.current_object_item = self.objects_tw.itemAt(eventPosition)

        contextMenu = QtWidgets.QMenu(self)

        if cmds.ls(sl=1):
            contextMenu.addAction(self.add_object_action)

        if self.current_object_item is not None:
            contextMenu.addAction(self.remove_object_action)

        action = contextMenu.exec_(child.mapToGlobal(eventPosition))

    def build_btn_callback(self):
        # [name]
        # [geo_type]
        # [distribute_type]
        # [scatter_amount]
        # [random]
        # [objects]

        objects = []

        for i in range(self.objects_tw.topLevelItemCount()):
            objects.append(pm.PyNode(self.objects_tw.topLevelItem(i).text(0)))

        mash_data = {
            'name': self.network_name_lble.text(),
            'geo_type': self.geo_type_cmbx.currentText(),
            'distribute_type': self.distribute_type_cmbx.currentText(),
            'scatter_amount': self.scatter_amount.value(),
            'random': self.add_random_cb.isChecked(),
            'objects': objects,
            'mesh': self.mesh_input_lble.text() if self.distribute_type_cmbx.currentText() == "Mesh" else None
        }

        mash_builder.create_mash_network(mash_data)


def main():
    try:
        cmds.deleteUI("MASHBuilderUI")
    except Exception:
        pass

    dialog = MASHBuilderUI()
    dialog.show()


if __name__ == "__main__":
    main()
