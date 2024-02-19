import sys
import importlib_resources

_gui_available = True

try:
    from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout)
    from PySide6 import QtCore
    from PySide6.QtWebEngineWidgets import QWebEngineView
    from PySide6.QtGui import QIcon
except ImportError:
    _gui_available = False


if _gui_available:

    class _webView(QWidget):
        def __init__(self):
            super().__init__()

            self.setWindowTitle("Reynard the Robot")
            icon_path = str(importlib_resources.files(__package__) / 'web_static' / 'rricon.ico')
            self.icon = QIcon(icon_path)
            self.setWindowIcon(self.icon)  

            self.layout = QVBoxLayout(self)

            self.webV = QWebEngineView()
            # self.fileDir = QtCore.QFileInfo("./docs.html").absoluteFilePath()
            # print(self.fileDir)
            # self.webV.load(QtCore.QUrl("file:///" + self.fileDir))
            self.webV.load(QtCore.QUrl("http://localhost:29201"))

            self.layout.addWidget(self.webV)

            screen_geometry = QApplication.primaryScreen().availableGeometry()
            self.resize(min(1040,screen_geometry.width()),min(890,screen_geometry.width()))


class ReynardGui:
    def __init__(self):
        pass

    @staticmethod
    def gui_available():
        return _gui_available        

    def run_gui(self):
        app = QApplication([])
        icon_path = str(importlib_resources.files(__package__) / 'web_static' / 'rricon.ico')
        icon = QIcon(icon_path)
        app.setWindowIcon(icon)  

        web = _webView()
        web.show()

        sys.exit(app.exec())