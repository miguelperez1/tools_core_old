from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import maya.cmds as cmds
import pymel.core as pm
import vray

from pyqt_commons import MWidgets
from maya_core.asset_manager.asset_browser import AssetBrowser

from maya_core.lighting_console import Widgets

reload(Widgets)
reload(MWidgets)
reload(AssetBrowser)


def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class LightingConsole(QtWidgets.QMainWindow):
    def __init__(self, parent=maya_main_window()):
        super(LightingConsole, self).__init__(parent)
        self.version = "1.0.0"

        self.setWindowTitle("Lighting Console")
        self.setObjectName("LightingConsole")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.log = Widgets.LogWidget.LogWidget()

        self.scale = 1
        self.res_x = 2550 * self.scale
        self.res_y = 1320 * self.scale

        self.setMinimumSize(self.res_x, self.res_y)

        if not cmds.objExists("l_rig"):
            cmds.group(n="l_rig", em=True)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.create_menu()

        self.log.result("Loaded Lighting Console version-" + self.version)

    def create_actions(self):
        pass

    def create_widgets(self):
        # Render settings
        self.render_settings_widget = Widgets.RenderSettingsWidget.RenderSettingsWidget()

        # Tool Buttons
        self.tool_buttons_widget = Widgets.ToolButtonsWidget.ToolButtonsWidget()

        # Render Layers
        self.render_layers_widget = Widgets.RenderLayersWidget.RenderLayersWidget()

        # Modifiers
        self.modifiers_widget = Widgets.ModifiersWidget.ModifiersWidget()

        # Console
        self.console_widget = Widgets.ConsoleWidget.ConsoleWidget()

        # Asset Browser
        self.asset_browser_widget = AssetBrowser.AssetBrowser(1.5, 6, libraries=['hdri', 'studio_lights', 'gobo_lights',
                                                                                 'clouds'])

        # Properties
        self.properties_widget = Widgets.PropertiesWidget.PropertiesWidget()

        # AOVs
        self.aovs_widget = Widgets.AOVsWidget.AOVsWidget()

        # Sets
        self.sets_widget = Widgets.SetsWidget.SetsWidget()

        # Sizing
        row_width = self.res_x * .95
        row_height = self.res_y * .875

        col1_width = row_width * .15
        col2_width = row_width * .675
        col3_width = row_width * .125

        self.tool_buttons_widget.setFixedHeight(self.res_y * .05)

        self.render_layers_widget.setFixedSize(col1_width, row_height * .225)
        self.modifiers_widget.setFixedSize(col1_width, row_height * .725)

        self.console_widget.setFixedSize(col2_width, row_height * .575)
        self.aovs_widget.setFixedSize(col2_width * .325, row_height * .375)
        self.asset_browser_widget.setFixedSize(col2_width * .635, row_height * .375)

        self.properties_widget.setMinimumSize(col3_width, row_height * .575)
        self.sets_widget.setMinimumSize(col3_width, row_height * .375)

    def create_layout(self):
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)
        main_layout.setSpacing(0)

        row_0_layout = QtWidgets.QHBoxLayout()
        row_0_layout.setSpacing(0)
        row_0_layout.addWidget(self.tool_buttons_widget)
        row_0_layout.addStretch()
        row_0_layout.addWidget(self.render_settings_widget)

        row_1_layout = QtWidgets.QHBoxLayout()
        row_1_layout.setSpacing(5)

        row1_col1_layout = QtWidgets.QVBoxLayout()
        row1_col1_layout.setSpacing(5)
        row1_col1_layout.addWidget(self.render_layers_widget)
        row1_col1_layout.addWidget(MWidgets.QHLine())
        row1_col1_layout.addWidget(self.modifiers_widget)

        row1_col2_layout = QtWidgets.QVBoxLayout()
        row1_col2_layout.setSpacing(5)
        row1_col2_layout.addWidget(self.console_widget)

        aov_browser_layout = QtWidgets.QHBoxLayout()
        aov_browser_layout.setSpacing(0)
        aov_browser_layout.addWidget(self.aovs_widget)
        aov_browser_layout.addWidget(MWidgets.QVLine())
        aov_browser_layout.addWidget(self.asset_browser_widget)

        row1_col2_layout.addWidget(MWidgets.QHLine())
        row1_col2_layout.addLayout(aov_browser_layout)

        row1_col3_layout = QtWidgets.QVBoxLayout()
        row1_col3_layout.setSpacing(5)
        row1_col3_layout.addWidget(self.properties_widget)
        row1_col3_layout.addWidget(MWidgets.QHLine())
        row1_col3_layout.addWidget(self.sets_widget)

        row_1_layout.addLayout(row1_col1_layout)
        row_1_layout.addWidget(MWidgets.QVLine())
        row_1_layout.addLayout(row1_col2_layout)
        row_1_layout.addWidget(MWidgets.QVLine())
        row_1_layout.addLayout(row1_col3_layout)

        main_layout.addWidget(MWidgets.QHLine())
        main_layout.addLayout(row_0_layout)
        main_layout.addWidget(MWidgets.QHLine())
        main_layout.addSpacing(10)
        main_layout.addLayout(row_1_layout)
        main_layout.addWidget(MWidgets.QHLine())
        main_layout.addSpacing(5)

        main_layout.addWidget(self.log.log_le)

    def create_connections(self):
        self.tool_buttons_widget.log_event.connect(self.push_log)
        self.render_layers_widget.log_event.connect(self.push_log)
        self.modifiers_widget.log_event.connect(self.push_log)
        self.console_widget.log_event.connect(self.push_log)
        self.aovs_widget.log_event.connect(self.push_log)
        self.properties_widget.log_event.connect(self.push_log)
        self.sets_widget.log_event.connect(self.push_log)

        # self.tool_buttons_widget.update_properties.connect(self.push_log)
        # self.render_layers_widget.update_properties.connect(self.update_properties_panel)
        # self.modifiers_widget.push_properties.connect(self.update_properties_panel)
        # self.console_widget.update_properties.connect(self.update_properties_panel)
        self.aovs_widget.push_properties.connect(self.update_properties_panel)
        # self.properties_widget.update_properties.connect(self.push_log)
        # self.sets_widget.update_properties.connect(self.push_log)

        self.tool_buttons_widget.light_created.connect(self.console_widget.create_light)
        self.asset_browser_widget.light_created.connect(self.console_widget.create_light)

    def update_properties_panel(self, properties_widget):
        self.properties_widget.set_properties(properties_widget)

    def push_log(self, log_type, log_message):
        if log_type == "info":
            self.log.info(log_message)
        if log_type == "result":
            self.log.result(log_message)
        if log_type == "warning":
            self.log.warning(log_message)
        if log_type == "error":
            self.log.error(log_message)

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


def main():
    try:
        cmds.deleteUI("LightingConsole")
    except Exception:
        pass

    dialog = LightingConsole()
    dialog.show()


if __name__ == "__main__":
    main()
