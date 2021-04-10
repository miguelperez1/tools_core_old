from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import maya.cmds as cmds


def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class QHLine(QtWidgets.QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)


class RenderManager(QtWidgets.QDialog):
    """
    Dialog used to demonstrates many of the standard dialogs available in Qt
    """

    def __init__(self, parent=maya_main_window()):
        super(RenderManager, self).__init__(parent)

        self.setWindowTitle("Render Holdout Tool")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.renderlayers_lbl = QtWidgets.QLabel("Render Layers")
        self.renderlayers_cmbx = QtWidgets.QComboBox()

        self.rsets_lbl = QtWidgets.QLabel("Render Sets")
        self.rsets_cmbx = QtWidgets.QComboBox()
        self.rsets_members_lbl = QtWidgets.QLabel("Set Objects")
        self.rsets_members_tv = QtWidgets.QTreeWidget()
        self.rsets_members_tv.setHeaderHidden(True)

        self.refresh_btn = QtWidgets.QPushButton("Refresh")

        self.create_rset_lbl = QtWidgets.QLabel("Enter Set Name:")
        self.create_rset_le = QtWidgets.QLineEdit()
        self.create_rset_btn = QtWidgets.QPushButton("Create Render Set")

        self.add_rset_btn = QtWidgets.QPushButton("Add to Set")

        self.matte_lbl = QtWidgets.QLabel("Matte Set")
        self.matte_cb = QtWidgets.QCheckBox()

        self.addmember_btn = QtWidgets.QPushButton("Add Object")

        self.update_layers()
        self.update_rsets()
        self.update_rset_members()

    def create_layout(self):
        renderlayer_layout = QtWidgets.QHBoxLayout()
        renderlayer_layout.addWidget(self.renderlayers_lbl)
        renderlayer_layout.addWidget(self.renderlayers_cmbx)

        matte_layout = QtWidgets.QHBoxLayout()
        matte_layout.addWidget(self.matte_lbl)
        matte_layout.addWidget(self.matte_cb)
        matte_layout.addStretch()

        rset_layout = QtWidgets.QHBoxLayout()
        rset_layout.addWidget(self.rsets_lbl)
        rset_layout.addWidget(self.rsets_cmbx)
        rset_layout.addWidget(self.matte_lbl)
        rset_layout.addWidget(self.matte_cb)
        rset_layout.addLayout(matte_layout)

        create_rset_layout = QtWidgets.QHBoxLayout()
        create_rset_layout.addWidget(self.create_rset_lbl)
        create_rset_layout.addWidget(self.create_rset_le)
        create_rset_layout.addWidget(self.create_rset_btn)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.addmember_btn)
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addStretch()

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(renderlayer_layout)
        main_layout.addWidget(QHLine())
        main_layout.addLayout(create_rset_layout)
        main_layout.addWidget(QHLine())
        main_layout.addLayout(rset_layout)
        main_layout.addWidget(QHLine())
        main_layout.addWidget(self.rsets_members_lbl)
        main_layout.addWidget(self.rsets_members_tv)
        main_layout.addLayout(matte_layout)
        main_layout.addLayout(btn_layout)

    def create_connections(self):
        self.renderlayers_cmbx.currentTextChanged.connect(self.switch_layer)
        self.refresh_btn.clicked.connect(self.update_all)
        self.create_rset_btn.clicked.connect(self.create_rset_btn_callback)
        self.rsets_cmbx.currentTextChanged.connect(self.update_rset_members)
        self.matte_cb.stateChanged.connect(self.matte_cb_callback)
        self.addmember_btn.clicked.connect(self.addmember_btn_callback)

    def matte_cb_callback(self):
        if self.rsets_cmbx.currentText() != "":
            cmds.editRenderLayerAdjustment("{}.matteObjects".format(self.rsets_cmbx.currentText()))
            cmds.setAttr("{}.matteObjects".format(self.rsets_cmbx.currentText()), self.matte_cb.isChecked())

    def switch_layer(self):
        try:
            cmds.editRenderLayerGlobals(currentRenderLayer=self.renderlayers_cmbx.currentText(),
                                        enableAutoAdjustments=True)
            self.update_rset_members()
        except TypeError:
            pass

    def update_layers(self):
        self.renderlayers_cmbx.clear()

        renderlayers = cmds.ls(type="renderLayer")
        try:
            renderlayers.remove("defaultRenderLayer")
        except TypeError:
            pass

        self.renderlayers_cmbx.addItems(renderlayers)

        current_layer = cmds.editRenderLayerGlobals(query=True, currentRenderLayer=True)

        for i in range(self.renderlayers_cmbx.count()):
            if current_layer == self.renderlayers_cmbx.itemText(i):
                self.renderlayers_cmbx.setCurrentIndex(i)
            else:
                continue

        self.update_rset_members()

    def update_rsets(self):
        self.rsets_cmbx.clear()

        rsets = []
        for objectset in cmds.ls(type="objectSet"):
            if objectset.endswith("_rset"):
                rsets.append(objectset)

        self.rsets_cmbx.addItems(rsets)

        self.update_rset_members()

    def update_rset_members(self):
        self.rsets_members_tv.clear()
        if self.rsets_cmbx.currentText() != "":
            # cmds.select(self.rsets_cmbx.currentText(), noExpand=True)
            members = cmds.sets(self.rsets_cmbx.currentText(), q=True)
            for m in members:
                item = QtWidgets.QTreeWidgetItem()
                item.setText(0, str(m))
                self.rsets_members_tv.addTopLevelItem(item)

            ismatte = cmds.getAttr("{}.matteObjects".format(self.rsets_cmbx.currentText()))
            self.matte_cb.setChecked(ismatte)

    def update_all(self):
        self.update_layers()
        self.update_rsets()
        self.update_rset_members()

    def create_rset_btn_callback(self):
        objects = cmds.selectedNodes()

        rset = self.create_rset_le.text() + "_rset"
        cmds.sets(name=rset)

        cmds.select(cl=True)

        cmds.addAttr(rset, longName="matteObjects", attributeType="bool")
        cmds.editRenderLayerAdjustment("{}.matteObjects".format(rset))

        for n in objects:
            cmds.connectAttr("{}.matteObjects".format(rset), "{}.rman_matteObject".format(n))
        self.update_all()
        self.create_rset_le.setText("")

    def addmember_btn_callback(self):
        if self.rsets_cmbx.currentText() != "":
            for n in cmds.selectedNodes():
                cmds.sets(n, add=self.rsets_cmbx.currentText())
                cmds.connectAttr("{}.matteObjects".format(self.rsets_cmbx.currentText()),
                                 "{}.rman_matteObject".format(n))

        self.update_rset_members()


def main():
    try:
        render_dialog.close()
        render_dialog.deleteLater()
    except:
        pass

    render_dialog = RenderManager()
    render_dialog.show()


if __name__ == "__main__":
    main()
