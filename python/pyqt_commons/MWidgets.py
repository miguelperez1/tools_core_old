from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui

from functools import partial


class QHLine(QtWidgets.QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)


class ScrollAreaWidget(QtWidgets.QWidget):
    def __init__(self, height):
        super(ScrollAreaWidget, self).__init__()

        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(height)
        self.scroll.setStyleSheet("border: none; background-color: rgb(50,50,50);")
        self.scroll.setContentsMargins(0, 0, 0, 0)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.scroll)

    def set_widget(self, widget):
        self.scroll.setWidget(widget)

    def remove_widget(self):
        self.scroll.takeWidget()


class ImagePushButton(QtWidgets.QPushButton):
    def __init__(self, size):
        super(ImagePushButton, self).__init__()
        self.set_default()
        self.size = size
        self.setFixedSize(self.size, self.size)
        self.setContentsMargins(5, 5, 5, 5)

    def set_image(self, path):
        icon = QtGui.QIcon(path)
        self.setIcon(icon)
        self.setIconSize(QtCore.QSize(self.size, self.size))

    def set_default(self):
        default_path = r'F:\share\tools\core\maya_core\asset_browser\icons\default.png'
        self.setIcon(QtGui.QPixmap(default_path).scaledToWidth(100, QtCore.Qt.SmoothTransformation))


class HeaderLabel(QtWidgets.QLabel):
    def __init__(self, text):
        super(HeaderLabel, self).__init__()
        self.setText(text)
        self.setStyleSheet("font: 20px")


class PreviewLabel(QtWidgets.QLabel):
    def __init__(self, *args, **kwargs):
        super(PreviewLabel, self).__init__(*args, **kwargs)
        self.set_default()
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setMinimumSize(1, 1)
        self.setContentsMargins(5, 5, 5, 5)
        self.setText('Test')

    def set_image(self, path, scale=160):
        self.pixmap = QtGui.QPixmap(path).scaledToWidth(scale, QtCore.Qt.SmoothTransformation)
        self.setPixmap(self.pixmap)

    def set_default(self):
        self.setPixmap(QtGui.QPixmap(r'F:\share\tools\core\asset_browser\icons\default.png').scaledToWidth(100,
                                                                                                           QtCore.Qt.SmoothTransformation))


class CustomColorButton(QtWidgets.QWidget):
    color_changed = QtCore.Signal(QtGui.QColor)

    def __init__(self, color=QtCore.Qt.white, parent=None):
        super(CustomColorButton, self).__init__(parent)
        self.autoFillBackground()
        self.setObjectName("CustomColorButton")

        self.create_control()

        self.set_size(100, 25)
        self.set_color(color)

    def create_control(self):
        window = cmds.window()
        color_slider_name = cmds.colorSliderGrp()

        self._color_slider_obj = omui.MQtUtil.findControl(color_slider_name)
        if self._color_slider_obj:
            self._color_slider_widget = wrapInstance(long(self._color_slider_obj), QtWidgets.QWidget)

            main_layout = QtWidgets.QVBoxLayout(self)
            main_layout.setObjectName("main_layout")
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.addWidget(self._color_slider_widget)

            self._slider_widget = self._color_slider_widget.findChild(QtWidgets.QWidget, "slider")
            if self._slider_widget:
                self._slider_widget.hide()

            self._color_widget = self._color_slider_widget.findChild(QtWidgets.QWidget, "port")

            cmds.colorSliderGrp(self.get_full_name(), e=True, changeCommand=partial(self.on_color_changed))

        cmds.deleteUI(window, window=True)

    def get_full_name(self):
        return omui.MQtUtil.fullName(long(self._color_slider_obj))

    def set_size(self, width, height):
        self._color_slider_widget.setFixedWidth(width)
        self._color_widget.setFixedHeight(height)

    def set_color(self, color):
        color = QtGui.QColor(color)
        cmds.colorSliderGrp(self.get_full_name(), e=True, rgbValue=(color.redF(), color.greenF(), color.blueF()))
        self.on_color_changed()

    def get_color(self):
        color = cmds.colorSliderGrp(self.get_full_name(), q=True, rgbValue=True)

        color = QtGui.QColor(color[0] * 255, color[1] * 255, color[2] * 255)
        return color

    def on_color_changed(self, *args):
        self.color_changed.emit(self.get_color())
