from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QSpinBox, QMessageBox, QStyle
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap
import os

from config import PRODUCTS_IMG_DIR
from controllers.cart_controller import CartController
from utils.ui_helpers import add_shadow


class CartItemWidget(QFrame):
    quantity_changed = pyqtSignal(object, int)
    remove_clicked = pyqtSignal(object)

    def __init__(self, item: dict):
        super().__init__()
        self.item = item
        self.product = item["product"]
        self.setObjectName("CartItem")
        self.setFixedHeight(120)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(16)

        img = QLabel()
        img.setFixedSize(96, 96)
        img.setStyleSheet("background: #F8FAFC; border-radius: 10px; color: #94A3B8;")
        img.setAlignment(Qt.AlignCenter)
        pix = self._load_pixmap()
        if pix:
            img.setPixmap(pix)
        else:
            img.setText("—")

        info = QVBoxLayout()
        info.setSpacing(4)

        name = QLabel(self.product.get("name", ""))
        name.setObjectName("CartItemName")
        name.setWordWrap(True)

        brand = QLabel(self.product.get("brand", ""))
        brand.setObjectName("CartItemBrand")

        info.addWidget(name)
        info.addWidget(brand)
        info.addStretch()

        qty_col = QVBoxLayout()
        qty_col.setSpacing(4)
        qty_lbl = QLabel("Количество")
        qty_lbl.setObjectName("Hint")

        self.spin = QSpinBox()
        self.spin.setMinimum(1)
        self.spin.setMaximum(999)
        self.spin.setValue(self.item["quantity"])
        self.spin.valueChanged.connect(lambda v: self.quantity_changed.emit(self.product["_id"], v))
        qty_col.addWidget(qty_lbl)
        qty_col.addWidget(self.spin)
        qty_col.addStretch()

        price_col = QVBoxLayout()
        price_col.setSpacing(4)
        unit = QLabel(f"{self.product.get('current_price', 0):.0f} ₽ / шт")
        unit.setObjectName("Hint")

        subtotal = QLabel(f"{self.item['subtotal']:.0f} ₽")
        subtotal.setObjectName("CartItemPrice")

        price_col.addWidget(unit)
        price_col.addWidget(subtotal)
        price_col.addStretch()

        btn_del = QPushButton()
        btn_del.setObjectName("IconButton")
        btn_del.setFixedSize(36, 36)
        btn_del.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        btn_del.setIconSize(QSize(18, 18))
        btn_del.setToolTip("Удалить из корзины")
        btn_del.clicked.connect(lambda: self.remove_clicked.emit(self.product["_id"]))

        lay.addWidget(img)
        lay.addLayout(info, 1)
        lay.addLayout(qty_col)
        lay.addSpacing(20)
        lay.addLayout(price_col)
        lay.addWidget(btn_del)

    def _load_pixmap(self):
        images = self.product.get("images", [])
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
                    return pix.scaled(96, 96, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        return None


class CartWindow(QWidget):
    back_requested = pyqtSignal()
    checkout_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.cart_ctrl = CartController()
        self.setWindowTitle("Гурман — Корзина")
        self.setGeometry(320, 80, 1080, 780)
        self._build_ui()
        self._load_items()

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

        title = QLabel("Корзина")
        title.setObjectName("PageTitle")

        top_lay.addWidget(btn_back)
        top_lay.addSpacing(12)
        top_lay.addWidget(title)
        top_lay.addStretch()

        root.addWidget(top)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        wrap = QWidget()
        wrap_lay = QVBoxLayout(wrap)
        wrap_lay.setContentsMargins(28, 24, 28, 24)
        wrap_lay.setSpacing(14)

        self.items_container = QVBoxLayout()
        self.items_container.setSpacing(12)
        wrap_lay.addLayout(self.items_container)
        wrap_lay.addStretch()

        scroll.setWidget(wrap)
        root.addWidget(scroll, 1)

        footer = QFrame()
        footer.setObjectName("Card")
        foot_lay = QHBoxLayout(footer)
        foot_lay.setContentsMargins(24, 16, 24, 16)
        foot_lay.setSpacing(16)

        lbl = QLabel("Итого:")
        lbl.setObjectName("SectionTitle")

        self.total_label = QLabel("0 ₽")
        self.total_label.setObjectName("CartTotal")

        self.btn_clear = QPushButton("Очистить")
        self.btn_clear.setObjectName("GhostButton")
        self.btn_clear.setFixedHeight(44)
        self.btn_clear.clicked.connect(self._on_clear)

        self.btn_checkout = QPushButton("Оформить заказ")
        self.btn_checkout.setFixedHeight(44)
        self.btn_checkout.setMinimumWidth(220)
        self.btn_checkout.clicked.connect(self._on_checkout)

        foot_lay.addWidget(lbl)
        foot_lay.addWidget(self.total_label)
        foot_lay.addStretch()
        foot_lay.addWidget(self.btn_clear)
        foot_lay.addWidget(self.btn_checkout)

        foot_wrap = QWidget()
        fw = QHBoxLayout(foot_wrap)
        fw.setContentsMargins(28, 0, 28, 24)
        fw.addWidget(footer)
        root.addWidget(foot_wrap)

        add_shadow(footer, blur=24, offset=6, alpha=25)

    def _load_items(self):
        while self.items_container.count():
            item = self.items_container.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        items = self.cart_ctrl.get_items()
        if not items:
            empty = QLabel("Ваша корзина пуста \nДобавьте товары из каталога.")
            empty.setObjectName("Hint")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet("padding: 60px; font-size: 14px;")
            self.items_container.addWidget(empty)
        else:
            for it in items:
                w = CartItemWidget(it)
                w.quantity_changed.connect(self._on_qty_change)
                w.remove_clicked.connect(self._on_remove)
                self.items_container.addWidget(w)

        self.total_label.setText(f"{self.cart_ctrl.total():.0f} ₽")

    def _on_qty_change(self, product_id, qty):
        self.cart_ctrl.update_quantity(product_id, qty)
        self._load_items()

    def _on_remove(self, product_id):
        self.cart_ctrl.remove(product_id)
        self._load_items()

    def _on_clear(self):
        confirm = QMessageBox.question(
            self, "Очистить корзину",
            "Удалить все товары?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.cart_ctrl.clear()
            self._load_items()

    def _on_checkout(self):
        if not self.cart_ctrl.get_items():
            QMessageBox.information(self, "Корзина", "Корзина пуста.")
            return
        QMessageBox.information(
            self, "Заказ",
            "Заказ оформлен! \n(в будущем — интеграция с магазинами)"
        )
        self.cart_ctrl.clear()
        self.checkout_requested.emit()