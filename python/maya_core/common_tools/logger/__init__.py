from PySide2 import QtWidgets

from pyqt_commons import MWidgets

reload(MWidgets)


class Logger(object):
    def __init__(self):
        self.status = False

    def info(self, message):
        out_message = None

        if self.status:
            out_message = "# Info:  " + ("-" * 15) + "  " + message
            print(out_message)

        return out_message

    def warning(self, message):
        out_message = "# Warning:  " + ("-" * 15) + "  " + message
        print(out_message)
        return out_message

    def error(self, message):
        out_message = "# Error:  " + ("-" * 15) + "  " + message
        print(out_message)
        return out_message

    def result(self, message):
        out_message = "# Result:  " + ("-" * 15) + "  " + message
        print(out_message)
        return out_message

    def debug(self, message):
        if self.status:
            out_message = "# Debug:  " + ("-" * 15) + "  " + message
            print(out_message)
            return out_message


class LogWidget(QtWidgets.QLineEdit):
    def __init__(self, parent=None):
        super(LogWidget, self).__init__(parent)

        self.log = Logger()
        self.log.status = True

        self.setObjectName("LogWidget")
        self.setEnabled(False)

    def info(self, message):
        self.setStyleSheet("color: rgb(135, 203, 203);")
        self.setText(self.log.info(message))

    def warning(self, message):
        self.setStyleSheet("color: rgb(223, 229, 39);")
        self.setText(self.log.warning(message))

    def error(self, message):
        self.setStyleSheet("color: rgb(244, 40, 40);")
        self.setText(self.log.error(message))

    def result(self, message):
        self.setStyleSheet("color: rgb(42, 180, 34);")
        self.setText(self.log.result(message))
