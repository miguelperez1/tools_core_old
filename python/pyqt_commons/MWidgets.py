from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui
import pymel.core as pm

import sys

from functools import partial


def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


def get_signals(source):
    cls = source if isinstance(source, type) else type(source)
    signal = type(QtCore.Signal())
    signals = []
    for name in dir(source):
        try:
            if isinstance(getattr(cls, name), signal):
                signals.append(name)
        except AttributeError:
            pass
    return signals


class QHLine(QtWidgets.QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.setContentsMargins(0, 0, 0, 0)


class QVLine(QtWidgets.QFrame):
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QtWidgets.QFrame.VLine)
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
    def __init__(self, size_x, size_y):
        super(ImagePushButton, self).__init__()
        self.set_default()
        self.size_x = size_x
        self.size_y = size_y
        self.setFixedSize(self.size_x, self.size_y)
        self.setContentsMargins(5, 5, 5, 5)
        # self.setStyleSheet("background-color: rgba(0, 0, 0, 0);")

    def set_image(self, path, scale=1):
        icon = QtGui.QIcon(path)
        self.setIcon(icon)
        self.setIconSize(QtCore.QSize(self.size_x * scale, self.size_y * scale))

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
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setMinimumSize(1, 1)
        self.setContentsMargins(0, 0, 0, 0)
        self.set_default()

    def set_image(self, path, scale=160):
        self.pixmap = QtGui.QPixmap(path).scaledToWidth(scale, QtCore.Qt.SmoothTransformation)
        self.setPixmap(self.pixmap)

    def set_default(self):
        self.setPixmap(QtGui.QPixmap(r'F:\share\tools\core\asset_browser\icons\default.png').scaledToWidth(100,
                                                                                                           QtCore.Qt.SmoothTransformation))


class CustomColorButton(QtWidgets.QWidget):
    color_changed = QtCore.Signal(QtGui.QColor)
    it_changed = QtCore.Signal()

    def __init__(self, color=QtCore.Qt.white, parent=None):
        super(CustomColorButton, self).__init__(parent)

        self.setObjectName("CustomColorButton")

        self.create_control()

        self.set_size(50, 14)
        self.set_color(color)

    def create_control(self):
        window = cmds.window()
        color_slider_name = cmds.colorSliderGrp()

        self._color_slider_obj = omui.MQtUtil.findControl(color_slider_name)
        if self._color_slider_obj:
            if sys.version_info.major >= 3:
                self._color_slider_widget = wrapInstance(int(self._color_slider_obj), QtWidgets.QWidget)
            else:
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
        if sys.version_info.major >= 3:
            return omui.MQtUtil.fullName(int(self._color_slider_obj))
        else:
            return omui.MQtUtil.fullName(long(self._color_slider_obj))

    def set_size(self, width, height):
        self._color_slider_widget.setFixedWidth(width)
        self._color_widget.setFixedHeight(height)

    def set_color(self, color):
        color = QtGui.QColor(color)

        cmds.colorSliderGrp(self.get_full_name(), e=True, rgbValue=(color.redF(), color.greenF(), color.blueF()))
        self.on_color_changed()

    def get_color(self):
        # color = cmds.colorSliderGrp(self._color_slider_widget.objectName(), q=True, rgbValue=True)
        color = cmds.colorSliderGrp(self.get_full_name(), q=True, rgbValue=True)

        color = QtGui.QColor(color[0] * 255, color[1] * 255, color[2] * 255)
        return color

    def on_color_changed(self, *args):
        self.color_changed.emit(self.get_color())


class ColorPickerTreeWidgetItemWidget(QtWidgets.QWidget):
    log_event = QtCore.Signal(str, str)
    clicked_event = QtCore.Signal(QtWidgets.QTreeWidgetItem)

    def __init__(self, width, height, light, item=None, color="white", *args, **kwargs):
        super(ColorPickerTreeWidgetItemWidget, self).__init__(*args, **kwargs)
        self.width = width
        self.height = height
        self.color = color
        self.item = item

        self.setObjectName("Color Widget")

        light = pm.PyNode(light)

        light = light.getShape()

        self.light = light

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.color_btn = QtWidgets.QPushButton()
        self.color_btn.setFixedSize(self.width * .75, self.height * .9)
        self.set_button_color()

    def create_layout(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setObjectName("main_layout")

        main_layout.addWidget(self.color_btn)

    def set_button_color(self, color=None, gamma=.454545):
        if color is not None:
            reset_light = True
        else:
            reset_light = False

        if not color:
            color = self.light.color.get()

        r, g, b = [pow(c, gamma) * 255 for c in color]
        new_color = (r, g, b)

        self.color_btn.setStyleSheet(
            'background-color: rgba(%s, %s, %s, 1.0);' % (new_color[0], new_color[1], new_color[2]))

        if reset_light:
            color = (pow(r / 255, 2.2), pow(g / 255, 2.2), pow(b / 255, 2.2))
            self.light.color.set(color)

    def create_connections(self):
        self.color_btn.clicked.connect(self.set_color)
        pass

    def set_color(self):
        light_color = self.light.color.get()
        color = pm.colorEditor(rgbValue=light_color)

        r, g, b, a = [float(c) for c in color.split()]

        color = (r, g, b)
        self.light.color.set(color)
        self.set_button_color(self.light.color.get())
