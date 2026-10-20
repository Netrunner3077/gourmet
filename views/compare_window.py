from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QGridLayout, QMessageBox, QStyle
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QIcon
import os

from config import PRODUCTS_IMG_DIR
from controllers.compare_controller import CompareController
from controllers.product_controller import ProductController


class CompareWindow(QWidget):
    back_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.prod_ctrl = ProductController()

        self.setWindowTitle("Гурман — Сравнение")
        self.setGeometry(240, 60, 1240, 820)
        self._build_ui()
        self._load()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        top = QWidget()
        top.setObjectName("TopBar")
        top.setFixedHeight(72)
        top_lay = QHBoxLayout(top)
        top_lay.setContentsMargins(24, 12, 24, 12)

        btn_back = QPushButton("Назад")
        btn_back.setObjectName("GhostButton")
        btn_back.setFixedHeight(38)
        btn_back.setIcon(self.style().standardIcon(QStyle.SP_ArrowBack))
        btn_back.setIconSize(QSize(16, 16))
        btn_back.clicked.connect(self.back_requested.emit)

        title = QLabel("Сравнение товаров")
        title.setObjectName("PageTitle")

        btn_clear = QPushButton("Очистить всё")
        btn_clear.setObjectName("GhostButton")
        btn_clear.setFixedHeight(38)
        btn_clear.clicked.connect(self._on_clear)

        top_lay.addWidget(btn_back)
        top_lay.addSpacing(12)
        top_lay.addWidget(title)
        top_lay.addStretch()
        top_lay.addWidget(btn_clear)

        root.addWidget(top)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.content = QWidget()
        self.grid = QGridLayout(self.content)
        self.grid.setContentsMargins(28, 24, 28, 24)
        self.grid.setSpacing(16)
        scroll.setWidget(self.content)
        root.addWidget(scroll, 1)

    def _load(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        ids = CompareController.get_selected()
        if len(ids) < 2:
            hint = QLabel(
                "Выберите минимум 2 товара для сравнения.\n\n"
                "На главной странице у каждой карточки есть кнопка сравнения — "
                "нажмите её, чтобы добавить товар."
            )
            hint.setObjectName("Hint")
            hint.setAlignment(Qt.AlignCenter)
            hint.setStyleSheet("padding: 80px; font-size: 14px;")
            self.grid.addWidget(hint, 0, 0, 1, 4)
            return

        products = self.prod_ctrl.get_products_by_ids(ids)

        for col, p in enumerate(products, start=1):
            self.grid.addWidget(self._make_header(p), 0, col)

        rows = [
            ("Бренд",        lambda p: p.get("brand", "—")),
            ("Категория",    lambda p: self.prod_ctrl.get_category_name(p["category_id"])),
            ("Цена",         lambda p: f"{p.get('current_price', 0):.2f} ₽"),
            ("Рейтинг",      lambda p: f"{p.get('rating', 0):.2f}  ({len(p.get('ratings', []))} оценок)"),
            ("Состав",       lambda p: p.get("composition", "—")),
            ("Аллергены",    lambda p: ", ".join(p.get("allergens", [])) or "нет"),
            ("Добавки",      lambda p: ", ".join(p.get("additives", [])) or "нет"),
        ]

        for row_idx, (label, getter) in enumerate(rows, start=1):
            lbl = QLabel(label)
            lbl.setObjectName("CompareCellLabel")
            lbl.setStyleSheet("background: #F8FAFC; border-radius: 10px; padding: 12px 14px;")
            lbl.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            lbl.setWordWrap(True)
            lbl.setMinimumWidth(140)
            self.grid.addWidget(lbl, row_idx, 0)

            for col_idx, p in enumerate(products, start=1):
                val = QLabel(str(getter(p)))
                val.setObjectName("CompareCellValue")
                val.setWordWrap(True)
                val.setAlignment(Qt.AlignTop | Qt.AlignLeft)
                val.setStyleSheet("background: #FFFFFF; border: 1px solid #EEF2F6; border-radius: 10px; padding: 12px 14px;")
                val.setMinimumWidth(220)
                self.grid.addWidget(val, row_idx, col_idx)

        for c in range(1, len(products) + 1):
            self.grid.setColumnStretch(c, 1)

    def _make_header(self, product: dict) -> QWidget:
        w = QFrame()
        w.setObjectName("CompareHeader")

        lay = QVBoxLayout(w)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(8)

        img = QLabel()
        img.setFixedHeight(120)
        img.setStyleSheet("background: #F8FAFC; border-radius: 10px; color: #94A3B8;")
        img.setAlignment(Qt.AlignCenter)
        pix = self._load_pixmap(product)
        if pix:
            img.setPixmap(pix)
        else:
            img.setText("нет фото")
        lay.addWidget(img)

        name = QLabel(product.get("name", ""))
        name.setObjectName("CompareProductName")
        name.setWordWrap(True)
        name.setAlignment(Qt.AlignCenter)
        lay.addWidget(name)

        btn = QPushButton("Убрать")
        btn.setObjectName("GhostButton")
        btn.setFixedHeight(30)
        btn.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        btn.setIconSize(QSize(14, 14))
        btn.clicked.connect(lambda: self._on_remove(product["_id"]))
        lay.addWidget(btn)
        return w

    def _load_pixmap(self, product: dict):
        images = product.get("images", [])
        if not images:
            return None
        filename = images[0]
        candidates = [
            filename,
            os.path.join(PRODUCTS_IMG_DIR, filename),
            os.path.join(PRODUCTS_IMG_DIR, os.path.basename(filename)),
        ]
        for path in candidates:
            if os.path.exists(path):
                pix = QPixmap(path)
                if not pix.isNull():
                    return pix.scaled(200, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        return None

    def _on_remove(self, product_id):
        CompareController.remove(product_id)
        self._load()

    def _on_clear(self):
        if not CompareController.get_selected():
            return
        confirm = QMessageBox.question(
            self, "Очистить", "Убрать все товары из сравнения?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            CompareController.clear()
            self._load()