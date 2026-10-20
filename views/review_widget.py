from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QWidget, QSizePolicy, QStyle
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont

from datetime import datetime

from views.widgets.star_rating import StarRatingDisplay
from utils.session import Session


class ReviewWidget(QFrame):
    """Карточка одного отзыва со всеми действиями."""
    like_clicked = pyqtSignal(object)
    dislike_clicked = pyqtSignal(object)
    comment_added = pyqtSignal(object, str)
    delete_clicked = pyqtSignal(object)

    def __init__(self, review: dict, parent=None):
        super().__init__(parent)
        self.review = review
        self.setObjectName("ReviewCard")
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(8)

        header = QHBoxLayout()
        header.setSpacing(8)

        author = QLabel(f" {self.review.get('author_login', 'Аноним')}")
        author.setObjectName("ReviewAuthor")
        author.setFont(QFont("Arial", 11, QFont.Bold))

        date = QLabel(self._format_date(self.review.get("created_at")))
        date.setObjectName("Hint")

        header.addWidget(author)
        header.addWidget(date)
        header.addStretch()

        stars = StarRatingDisplay(self.review.get("rating", 0), size=14)
        header.addWidget(stars)

        user = Session.get_user() or {}
        if (user.get("_id") == self.review.get("user_id")
                or user.get("is_admin")):
            btn_del = QPushButton()
            btn_del.setObjectName("IconButton")
            btn_del.setFixedSize(28, 28)
            btn_del.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
            btn_del.setIconSize(QSize(14, 14))
            btn_del.setToolTip("Удалить отзыв")
            header.addWidget(btn_del)

        root.addLayout(header)

        text = QLabel(self.review.get("text", ""))
        text.setObjectName("ReviewText")
        text.setWordWrap(True)
        text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        root.addWidget(text)

        actions = QHBoxLayout()
        actions.setSpacing(6)

        self.btn_like = QPushButton(
            f" {self.review.get('likes', 0)}"
        )
        self.btn_like.setObjectName("ReactButton")
        self.btn_like.setFixedHeight(28)
        self.btn_like.clicked.connect(
            lambda: self.like_clicked.emit(self.review["_id"])
        )

        self.btn_dislike = QPushButton(
            f" {self.review.get('dislikes', 0)}"
        )
        self.btn_dislike.setObjectName("ReactButton")
        self.btn_dislike.setFixedHeight(28)
        self.btn_dislike.clicked.connect(
            lambda: self.dislike_clicked.emit(self.review["_id"])
        )

        self.btn_toggle_comments = QPushButton(
            f" Комментарии ({len(self.review.get('comments', []))})"
        )
        self.btn_toggle_comments.setObjectName("ReactButton")
        self.btn_toggle_comments.setFixedHeight(28)
        self.btn_toggle_comments.setCheckable(True)
        self.btn_toggle_comments.toggled.connect(self._toggle_comments)

        actions.addWidget(self.btn_like)
        actions.addWidget(self.btn_dislike)
        actions.addWidget(self.btn_toggle_comments)
        actions.addStretch()
        root.addLayout(actions)

        self.comments_box = QWidget()
        cb_layout = QVBoxLayout(self.comments_box)
        cb_layout.setContentsMargins(20, 4, 0, 4)
        cb_layout.setSpacing(4)

        for c in self.review.get("comments", []):
            cb_layout.addWidget(self._make_comment_label(c))

        self.input_row = QHBoxLayout()
        self.comment_input = QLineEdit()
        self.comment_input.setPlaceholderText("Написать комментарий...")
        btn_send = QPushButton("Отправить")
        btn_send.setFixedHeight(30)
        btn_send.clicked.connect(self._on_send_comment)
        self.input_row.addWidget(self.comment_input, 1)
        self.input_row.addWidget(btn_send)
        cb_layout.addLayout(self.input_row)

        self.comments_box.setVisible(False)
        root.addWidget(self.comments_box)

    def _make_comment_label(self, c: dict) -> QLabel:
        date = self._format_date(c.get("created_at"))
        text = (
            f"<b>{c.get('author_login', 'Аноним')}</b> "
            f"<span style='color:#9CA3AF;'>· {date}</span><br>"
            f"{c.get('text', '')}"
        )
        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setStyleSheet(
            "background: #FFFDF8; border-radius: 8px;"
            "padding: 6px 10px; color: #374151;"
        )
        return lbl

    def _toggle_comments(self, checked: bool):
        self.comments_box.setVisible(checked)

    def _on_send_comment(self):
        text = self.comment_input.text().strip()
        if not text:
            return
        self.comment_added.emit(self.review["_id"], text)
        self.comment_input.clear()

    @staticmethod
    def _format_date(dt) -> str:
        if not isinstance(dt, datetime):
            return ""
        return dt.strftime("%d.%m.%Y %H:%M")