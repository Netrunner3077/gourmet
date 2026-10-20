from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QFormLayout, QMessageBox, QHBoxLayout, QStyle
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal, QSize

from controllers.auth_controller import AuthController


class RegisterWindow(QWidget):
    go_to_login = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.auth = AuthController()
        self._build_ui()

    def _build_ui(self):
        self.setWindowTitle("Гурман — Регистрация")
        self.setGeometry(600, 300, 400, 320)
        self.setFixedSize(400, 320)

        title = QLabel("Регистрация")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Bold))

        self.login_edit = QLineEdit()
        self.pw1 = QLineEdit()
        self.pw1.setEchoMode(QLineEdit.Password)
        self.pw2 = QLineEdit()
        self.pw2.setEchoMode(QLineEdit.Password)

        form = QFormLayout()
        form.addRow("Логин:", self.login_edit)
        form.addRow("Пароль:", self.pw1)
        form.addRow("Повтор пароля:", self.pw2)

        self.btn_create = QPushButton("Создать аккаунт")
        self.btn_create.clicked.connect(self._on_register)

        self.btn_back = QPushButton("Назад ко входу")
        self.btn_back.setIcon(self.style().standardIcon(QStyle.SP_ArrowBack))
        self.btn_back.setIconSize(QSize(16, 16))
        self.btn_back.clicked.connect(self.go_to_login.emit)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addLayout(form)
        layout.addWidget(self.btn_create)
        layout.addWidget(self.btn_back)
        self.setLayout(layout)

    def _on_register(self):
        login = self.login_edit.text().strip()
        pw1 = self.pw1.text()
        pw2 = self.pw2.text()

        ok, msg = self.auth.register(login, pw1, pw2)
        if ok:
            QMessageBox.information(self, "Успех", msg)
            self.go_to_login.emit()
        else:
            QMessageBox.warning(self, "Ошибка", msg)