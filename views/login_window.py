from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QMessageBox, QFormLayout, QStyle
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, pyqtSignal, QSize

from controllers.auth_controller import AuthController


class LoginWindow(QWidget):
    login_success = pyqtSignal()
    go_to_register = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.auth = AuthController()
        self._build_ui()

    def _build_ui(self):
        self.setWindowTitle("Гурман — Вход")
        self.setGeometry(600, 300, 380, 260)
        self.setFixedSize(380, 260)

        title = QLabel("ГУРМАН")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 18, QFont.Bold))

        self.login_edit = QLineEdit()
        self.login_edit.setPlaceholderText("Логин")

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Пароль")
        self.password_edit.setEchoMode(QLineEdit.Password)

        self.btn_show_pw = QPushButton()
        self.btn_show_pw.setFixedWidth(32)
        self.btn_show_pw.setCheckable(True)
        self.btn_show_pw.setIcon(self.style().standardIcon(QStyle.SP_DialogYesButton))
        self.btn_show_pw.setIconSize(QSize(16, 16))
        self.btn_show_pw.toggled.connect(self._toggle_password)
        self.btn_show_pw.setToolTip("Показать/скрыть пароль")

        pw_row = QHBoxLayout()
        pw_row.addWidget(self.password_edit)
        pw_row.addWidget(self.btn_show_pw)

        form = QFormLayout()
        form.addRow("Логин:", self.login_edit)
        form.addRow("Пароль:", pw_row)

        self.btn_login = QPushButton("Войти")
        self.btn_login.clicked.connect(self._on_login)

        self.btn_register = QPushButton("Регистрация")
        self.btn_register.clicked.connect(self.go_to_register.emit)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addLayout(form)
        layout.addWidget(self.btn_login)
        layout.addWidget(self.btn_register)
        self.setLayout(layout)

    def _toggle_password(self, checked: bool):
        self.password_edit.setEchoMode(
            QLineEdit.Normal if checked else QLineEdit.Password
        )

    def _on_login(self):
        login = self.login_edit.text().strip()
        password = self.password_edit.text()
        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль.")
            return
        ok, msg = self.auth.login(login, password)
        if ok:
            self.login_success.emit()
        else:
            QMessageBox.warning(self, "Ошибка", msg)

    def clear_fields(self):
        self.login_edit.clear()
        self.password_edit.clear()