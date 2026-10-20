import sys
import os
import PyQt5

_qt_plugin_path = os.path.join(os.path.dirname(PyQt5.__file__), "Qt5", "plugins")
os.environ["QT_PLUGIN_PATH"] = _qt_plugin_path
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = os.path.join(_qt_plugin_path, "platforms")

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from models.database import Database, init_indexes
from views.login_window import LoginWindow
from views.register_window import RegisterWindow
from views.main_window import MainWindow

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STYLE_PATH = os.path.join(PROJECT_ROOT, "resources", "styles", "style.qss")


def load_stylesheet(app: QApplication) -> str:
    if os.path.exists(STYLE_PATH):
        with open(STYLE_PATH, "r", encoding="utf-8") as f:
            qss = f.read()
        app.setStyleSheet(qss)
        print(f"[UI] Стиль загружен: {STYLE_PATH}")
    else:
        print(f"[UI] Внимание: файл стилей не найден — {STYLE_PATH}")


class AppCoordinator:
    def __init__(self):
        self.login_window = None
        self.register_window = None
        self.main_window = None

    def show_login(self):
        if self.main_window:
            self.main_window.close()
        if self.register_window:
            self.register_window.close()

        self.login_window = LoginWindow()
        self.login_window.login_success.connect(self.show_main)
        self.login_window.go_to_register.connect(self.show_register)
        self.login_window.show()

    def show_register(self):
        self.login_window.close()
        self.register_window = RegisterWindow()
        self.register_window.go_to_login.connect(self.show_login)
        self.register_window.show()

    def show_main(self):
        self.login_window.close()
        self.main_window = MainWindow()
        self.main_window.logout_requested.connect(self.show_login)
        self.main_window.show()


def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    load_stylesheet(app)

    try:
        Database()
        init_indexes()
    except RuntimeError as e:
        print(f"[FATAL] {e}")
        sys.exit(1)

    coordinator = AppCoordinator()
    coordinator.show_login()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()