from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QFileDialog, QMessageBox, QLineEdit,
    QGridLayout, QStyle
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QIcon

from controllers.profile_controller import ProfileController
from controllers.product_controller import ProductController
from controllers.review_controller import ReviewController
from utils.image_utils import get_avatar_path, make_placeholder_avatar
from utils.session import Session
from views.product_card import ProductCard


class ProfileWindow(QWidget):
    back_requested = pyqtSignal()
    logout_requested = pyqtSignal()
    product_selected = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.profile_ctrl = ProfileController()
        self.product_ctrl = ProductController()
        self.review_ctrl = ReviewController()

        self.setWindowTitle("Гурман — Профиль")
        self.setGeometry(380, 60, 1140, 860)
        self._build_ui()
        self._load_all()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        top = QWidget()
        top.setObjectName("TopBar")
        top.setFixedHeight(64)
        top_lay = QHBoxLayout(top)
        top_lay.setContentsMargins(20, 8, 20, 8)

        btn_back = QPushButton("На главную")
        btn_back.setObjectName("GhostButton")
        btn_back.setFixedHeight(36)
        btn_back.setIcon(self.style().standardIcon(QStyle.SP_ArrowBack))
        btn_back.setIconSize(QSize(16, 16))
        btn_back.clicked.connect(self.back_requested.emit)

        title = QLabel("Профиль")
        title.setObjectName("PageTitle")

        btn_logout = QPushButton("Выйти из аккаунта")
        btn_logout.setObjectName("GhostButton")
        btn_logout.setFixedHeight(36)
        btn_logout.clicked.connect(self._on_logout)

        top_lay.addWidget(btn_back)
        top_lay.addSpacing(16)
        top_lay.addWidget(title)
        top_lay.addStretch()
        top_lay.addWidget(btn_logout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.content_lay = QVBoxLayout(content)
        self.content_lay.setContentsMargins(24, 24, 24, 24)
        self.content_lay.setSpacing(20)

        header_card = QFrame()
        header_card.setObjectName("Card")
        header_lay = QHBoxLayout(header_card)
        header_lay.setContentsMargins(28, 24, 28, 24)
        header_lay.setSpacing(28)

        avatar_col = QVBoxLayout()
        avatar_col.setSpacing(10)

        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(140, 140)
        self.avatar_label.setAlignment(Qt.AlignCenter)
        avatar_col.addWidget(self.avatar_label, alignment=Qt.AlignHCenter)

        btn_change_avatar = QPushButton("Изменить аватар")
        btn_change_avatar.setObjectName("GhostButton")
        btn_change_avatar.setFixedHeight(34)
        btn_change_avatar.clicked.connect(self._on_change_avatar)
        avatar_col.addWidget(btn_change_avatar)

        header_lay.addLayout(avatar_col)

        info_col = QVBoxLayout()
        info_col.setSpacing(8)

        self.login_label = QLabel("—")
        self.login_label.setObjectName("ProfileLogin")
        self.login_label.setFont(QFont("Segoe UI", 20, QFont.Bold))

        self.joined_label = QLabel("")
        self.joined_label.setObjectName("Hint")

        info_col.addWidget(self.login_label)
        info_col.addWidget(self.joined_label)
        info_col.addStretch()

        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)

        self.stat_reviews = self._make_stat_box("", "Отзывы", "0")
        self.stat_comments = self._make_stat_box("", "Комментарии", "0")
        self.stat_favorites = self._make_stat_box("", "В избранном", "0")

        stats_row.addWidget(self.stat_reviews)
        stats_row.addWidget(self.stat_comments)
        stats_row.addWidget(self.stat_favorites)
        stats_row.addStretch()

        info_col.addLayout(stats_row)

        header_lay.addLayout(info_col, 1)

        self.content_lay.addWidget(header_card)

        fav_title = QLabel("Избранные товары")
        fav_title.setObjectName("SectionTitle")
        self.content_lay.addWidget(fav_title)

        self.fav_container = QWidget()
        self.fav_grid = QGridLayout(self.fav_container)
        self.fav_grid.setContentsMargins(0, 0, 0, 0)
        self.fav_grid.setSpacing(16)
        self.fav_grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.content_lay.addWidget(self.fav_container)

        reviews_title = QLabel("Мои отзывы")
        reviews_title.setObjectName("SectionTitle")
        self.content_lay.addWidget(reviews_title)

        self.reviews_container = QVBoxLayout()
        self.reviews_container.setSpacing(10)
        self.content_lay.addLayout(self.reviews_container)

        pwd_card = QFrame()
        pwd_card.setObjectName("Card")
        pwd_lay = QVBoxLayout(pwd_card)
        pwd_lay.setContentsMargins(24, 20, 24, 20)
        pwd_lay.setSpacing(12)

        pwd_title = QLabel("Смена пароля")
        pwd_title.setObjectName("SectionTitle")
        pwd_lay.addWidget(pwd_title)

        form = QHBoxLayout()
        form.setSpacing(12)

        self.old_pwd = QLineEdit()
        self.old_pwd.setPlaceholderText("Старый пароль")
        self.old_pwd.setEchoMode(QLineEdit.Password)
        self.old_pwd.setMinimumWidth(200)

        self.new_pwd1 = QLineEdit()
        self.new_pwd1.setPlaceholderText("Новый пароль")
        self.new_pwd1.setEchoMode(QLineEdit.Password)
        self.new_pwd1.setMinimumWidth(200)

        self.new_pwd2 = QLineEdit()
        self.new_pwd2.setPlaceholderText("Повтор нового пароля")
        self.new_pwd2.setEchoMode(QLineEdit.Password)
        self.new_pwd2.setMinimumWidth(200)

        btn_change_pwd = QPushButton("Изменить пароль")
        btn_change_pwd.setFixedHeight(38)
        btn_change_pwd.clicked.connect(self._on_change_password)

        form.addWidget(self.old_pwd, 1)
        form.addWidget(self.new_pwd1, 1)
        form.addWidget(self.new_pwd2, 1)
        form.addWidget(btn_change_pwd)

        pwd_lay.addLayout(form)
        self.content_lay.addWidget(pwd_card)

        self.content_lay.addStretch()

        scroll.setWidget(content)
        root.addWidget(top)
        root.addWidget(scroll, 1)

    def _make_stat_box(self, emoji: str, label_text: str, value: str) -> QFrame:
        box = QFrame()
        box.setObjectName("StatBox")
        box.setFixedSize(150, 90)

        lay = QVBoxLayout(box)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(2)

        top = QLabel(f"{emoji}  {label_text}")
        top.setObjectName("StatLabel")
        top.setStyleSheet("color:#64748B; font-size:11px;")

        self_val = QLabel(value)
        self_val.setObjectName("StatValue")
        self_val.setFont(QFont("Segoe UI", 22, QFont.Bold))
        self_val.setStyleSheet("color:#047857;")

        lay.addWidget(top)
        lay.addWidget(self_val)
        box.setProperty("value_label", self_val)
        return box

    def _load_all(self):
        self._load_user_header()
        self._load_favorites()
        self._load_my_reviews()
        self._load_stats()

    def _load_user_header(self):
        user = self.profile_ctrl.get_current_user()
        if not user:
            return

        self.login_label.setText(f" {user['login']}")

        joined = user.get("created_at")
        if joined:
            try:
                self.joined_label.setText(
                    f"На Гурмане с {joined.strftime('%d.%m.%Y')}"
                )
            except Exception:
                self.joined_label.setText("")

        avatar_path = user.get("avatar")
        pix = get_avatar_path(avatar_path, size=140)
        if not pix:
            pix = make_placeholder_avatar(user["login"][:1] or "?", 140)
        self.avatar_label.setPixmap(pix)

    def _load_stats(self):
        s = self.profile_ctrl.get_stats()
        self.stat_reviews.property("value_label").setText(str(s["reviews"]))
        self.stat_comments.property("value_label").setText(str(s["comments"]))
        self.stat_favorites.property("value_label").setText(str(s["favorites"]))

    def _load_favorites(self):
        while self.fav_grid.count():
            item = self.fav_grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        favorites = self.profile_ctrl.get_favorites()
        if not favorites:
            empty = QLabel("В избранном пока пусто. Добавьте товары ⭐")
            empty.setObjectName("Hint")
            empty.setStyleSheet("padding: 12px 0;")
            self.fav_grid.addWidget(empty, 0, 0, 1, 4)
            return

        for i, product in enumerate(favorites):
            card = ProductCard(product)
            card.clicked.connect(
                lambda p: self.product_selected.emit(p["_id"])
            )
            row, col = divmod(i, 4)
            self.fav_grid.addWidget(card, row, col)

    def _load_my_reviews(self):
        while self.reviews_container.count():
            item = self.reviews_container.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        reviews = self.profile_ctrl.get_my_reviews()
        if not reviews:
            empty = QLabel("Вы ещё не оставили ни одного отзыва.")
            empty.setObjectName("Hint")
            empty.setStyleSheet("padding: 8px 0;")
            self.reviews_container.addWidget(empty)
            return

        for r in reviews:
            self.reviews_container.addWidget(self._make_review_row(r))

    def _make_review_row(self, review: dict) -> QFrame:
        row = QFrame()
        row.setObjectName("ReviewCard")

        lay = QVBoxLayout(row)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(6)

        top = QHBoxLayout()
        top.setSpacing(10)

        product_name = QLabel(f" {review.get('product_name', '—')}")
        product_name.setFont(QFont("Segoe UI", 12, QFont.Bold))
        product_name.setStyleSheet("color: #0F172A;")

        stars = QLabel("★" * review.get("rating", 0) +
                       "☆" * (5 - review.get("rating", 0)))
        stars.setStyleSheet("color: #F59E0B; font-size: 14px;")

        date = QLabel("")
        if review.get("created_at"):
            try:
                date.setText(
                    review["created_at"].strftime("%d.%m.%Y %H:%M")
                )
            except Exception:
                pass
        date.setObjectName("Hint")

        top.addWidget(product_name)
        top.addWidget(stars)
        top.addStretch()
        top.addWidget(date)

        text = QLabel(review.get("text", ""))
        text.setWordWrap(True)
        text.setStyleSheet("color: #334155;")

        actions = QHBoxLayout()
        actions.setSpacing(6)

        btn_open = QPushButton("Открыть товар")
        btn_open.setObjectName("ReactButton")
        btn_open.setFixedHeight(28)
        btn_open.clicked.connect(
            lambda _, pid=review["product_id"]: self.product_selected.emit(pid)
        )

        btn_del = QPushButton("Удалить")
        btn_del.setObjectName("ReactButton")
        btn_del.setFixedHeight(28)
        btn_del.clicked.connect(
            lambda _, rid=review["_id"]: self._on_delete_my_review(rid)
        )

        actions.addWidget(btn_open)
        actions.addWidget(btn_del)
        actions.addStretch()

        lay.addLayout(top)
        lay.addWidget(text)
        lay.addLayout(actions)
        return row

    def _on_change_avatar(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "",
            "Изображения (*.png *.jpg *.jpeg *.bmp)"
        )
        if not path:
            return
        ok, msg = self.profile_ctrl.update_avatar(path)
        if not ok:
            QMessageBox.warning(self, "Ошибка", msg)
            return
        QMessageBox.information(self, "Готово", msg)
        self._load_user_header()

    def _on_change_password(self):
        old = self.old_pwd.text()
        new1 = self.new_pwd1.text()
        new2 = self.new_pwd2.text()

        if not old or not new1 or not new2:
            QMessageBox.warning(self, "Ошибка",
                                "Заполните все поля пароля.")
            return

        ok, msg = self.profile_ctrl.change_password(old, new1, new2)
        if not ok:
            QMessageBox.warning(self, "Ошибка", msg)
            return
        QMessageBox.information(self, "Готово", msg)
        self.old_pwd.clear()
        self.new_pwd1.clear()
        self.new_pwd2.clear()

    def _on_delete_my_review(self, review_id):
        confirm = QMessageBox.question(
            self, "Удаление отзыва",
            "Удалить этот отзыв?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return
        ok, msg = self.review_ctrl.delete_review(review_id)
        if not ok:
            QMessageBox.warning(self, "Ошибка", msg)
            return
        self._load_my_reviews()
        self._load_stats()

    def _on_logout(self):
        Session.logout()
        self.logout_requested.emit()