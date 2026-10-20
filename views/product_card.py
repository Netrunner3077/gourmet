import os

from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal

from config import PRODUCTS_IMG_DIR
from utils.ui_helpers import badge
from utils.composition_analyzer import analyze as _analyze
from controllers.product_controller import ProductController
from controllers.compare_controller import CompareController


class ProductCard(QFrame):
    clicked = pyqtSignal(dict)
    fav_toggled = pyqtSignal(object)
    compare_toggled = pyqtSignal(object)

    def __init__(self, product: dict, images_dir: str = PRODUCTS_IMG_DIR, parent=None):
        super().__init__(parent)
        self.product = product
        self.images_dir = images_dir
        self.product_ctrl = ProductController()
        self.setObjectName("ProductCard")
        self.setFixedSize(240, 350)
        self.setCursor(Qt.PointingHandCursor)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 14)
        root.setSpacing(10)

        img_wrap = QFrame()
        img_wrap.setFixedSize(216, 180)
        img_wrap.setStyleSheet("background: transparent;")

        img_label = QLabel(img_wrap)
        img_label.setObjectName("ProductImage")
        img_label.setGeometry(0, 0, 216, 180)
        img_label.setAlignment(Qt.AlignCenter)
        pix = self._load_pixmap(216, 180)
        if pix:
            img_label.setPixmap(pix)
        else:
            img_label.setText("нет фото")

        rating = self.product.get("rating", 0)
        if rating > 0:
            r_badge = badge(f"★ {rating:.1f}", "#0F172A", "#FFFFFF")
            r_badge.setParent(img_wrap)
            r_badge.move(160, 8)
            r_badge.adjustSize()
            r_badge.raise_()

        _risk = _analyze(self.product.get("composition", ""))
        if _risk["risk_level"] == "high":
            risk_badge = badge("⚠ высокий риск", "#B91C1C", "#FFFFFF")
            risk_badge.setParent(img_wrap)
            risk_badge.move(8, 152)
            risk_badge.adjustSize()
            risk_badge.raise_()
        elif _risk["risk_level"] == "medium":
            risk_badge = badge("средний риск", "#B45309", "#FFFFFF")
            risk_badge.setParent(img_wrap)
            risk_badge.move(8, 152)
            risk_badge.adjustSize()
            risk_badge.raise_()

        self.btn_fav = QPushButton("☆", img_wrap)
        self.btn_fav.setObjectName("CardFavButton")
        self.btn_fav.setFixedSize(32, 32)
        self.btn_fav.move(8, 8)
        self.btn_fav.setCursor(Qt.PointingHandCursor)
        self.btn_fav.setStyleSheet(
            "QPushButton#CardFavButton {"
            " background: rgba(255,255,255,0.9);"
            " border: none; border-radius: 16px;"
            " font-size: 16px; color: #64748B; padding: 0;"
            "}"
            "QPushButton#CardFavButton:hover {"
            " background: #FEE2E2; color: #DC2626;"
            "}"
        )
        self.btn_fav.clicked.connect(
            lambda: self.fav_toggled.emit(self.product["_id"])
        )
        self._refresh_fav()

        root.addWidget(img_wrap)

        name = QLabel(self._shorten(self.product.get("name", ""), 52))
        name.setObjectName("ProductName")
        name.setWordWrap(True)
        name.setFixedHeight(36)
        name.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        root.addWidget(name)

        brand = QLabel(self.product.get("brand", ""))
        brand.setObjectName("ProductBrand")
        root.addWidget(brand)

        root.addStretch()

        bottom = QHBoxLayout()
        bottom.setSpacing(6)

        price = QLabel(f"{self.product.get('current_price', 0):.0f} ₽")
        price.setObjectName("ProductPrice")

        self.btn_cmp = QPushButton("")
        self.btn_cmp.setObjectName("IconButton")
        self.btn_cmp.setFixedSize(30, 30)
        self.btn_cmp.setCursor(Qt.PointingHandCursor)
        self.btn_cmp.setToolTip("Добавить к сравнению")
        self.btn_cmp.clicked.connect(
            lambda: self.compare_toggled.emit(self.product["_id"])
        )
        self._refresh_cmp_style()

        bottom.addWidget(price)
        bottom.addStretch()
        bottom.addWidget(self.btn_cmp)
        root.addLayout(bottom)

    def _load_pixmap(self, w: int, h: int):
        images = self.product.get("images", [])
        if not images:
            return None
        filename = images[0]
        candidates = [
            filename,
            os.path.join(self.images_dir, filename),
            os.path.join(self.images_dir, os.path.basename(filename)),
        ]
        for path in candidates:
            if os.path.exists(path):
                pix = QPixmap(path)
                if not pix.isNull():
                    return pix.scaled(
                        w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
        return None

    def _shorten(self, text: str, limit: int) -> str:
        return text if len(text) <= limit else text[:limit - 1] + "…"

    def _refresh_fav(self):
        if self.product_ctrl.is_favorite(self.product["_id"]):
            self.btn_fav.setText("★")
            self.btn_fav.setStyleSheet(
                "QPushButton#CardFavButton {"
                " background: #FEF3C7;"
                " border: none; border-radius: 16px;"
                " font-size: 16px; color: #F59E0B; padding: 0;"
                "}"
            )
        else:
            self.btn_fav.setText("☆")
            self.btn_fav.setStyleSheet(
                "QPushButton#CardFavButton {"
                " background: rgba(255,255,255,0.9);"
                " border: none; border-radius: 16px;"
                " font-size: 16px; color: #64748B; padding: 0;"
                "}"
                "QPushButton#CardFavButton:hover {"
                " background: #FEE2E2; color: #DC2626;"
                "}"
            )

    def _refresh_cmp_style(self):
        sel = CompareController.is_selected(self.product["_id"])
        if sel:
            self.btn_cmp.setStyleSheet(
                "background: #ECFDF5; color: #047857;"
                " border: 1px solid #A7F3D0; border-radius: 8px;"
                " font-size: 14px; padding: 0;"
            )
        else:
            self.btn_cmp.setStyleSheet(
                "background: transparent; color: #94A3B8;"
                " border: none; border-radius: 8px;"
                " font-size: 14px; padding: 0;"
            )

    def refresh_fav(self):
        self._refresh_fav()

    def refresh_compare(self):
        self._refresh_cmp_style()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.product)