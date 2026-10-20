import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QTextEdit, QFrame, QStyle, QSizePolicy, QMessageBox,
    QDialog, QDialogButtonBox, QDoubleSpinBox, QComboBox, QFormLayout
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QFont

from bson import ObjectId

from controllers.product_controller import ProductController
from controllers.review_controller import ReviewController
from controllers.price_controller import PriceController
from controllers.compare_controller import CompareController

from views.widgets.star_rating import StarRatingDisplay, StarRatingInput
from views.review_widget import ReviewWidget
from views.price_chart import PriceChart

from utils.session import Session
from utils.composition_analyzer import analyze as analyze_composition

from config import PRODUCTS_IMG_DIR


class ProductWindow(QWidget):
    back_requested = pyqtSignal()

    def __init__(self, product_id: ObjectId):
        super().__init__()
        self.product_id = product_id
        self.product_ctrl = ProductController()
        self.review_ctrl = ReviewController()

        self.product = self.product_ctrl.get_product(product_id)
        if not self.product:
            QMessageBox.critical(self, "Ошибка", "Товар не найден.")
            self.back_requested.emit()
            return

        self._syncing_rating = False

        self.setWindowTitle(f"Гурман — {self.product['name']}")
        self.setGeometry(420, 80, 1080, 820)
        self._build_ui()
        self._sync_star_widgets(self.product_ctrl.get_user_rating(self.product))
        self._load_reviews()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        top = QWidget()
        top.setObjectName("TopBar")
        top.setFixedHeight(64)
        top_lay = QHBoxLayout(top)
        top_lay.setContentsMargins(20, 8, 20, 8)

        btn_back = QPushButton("Назад")
        btn_back.setObjectName("GhostButton")
        btn_back.setFixedHeight(36)
        btn_back.setIcon(self.style().standardIcon(QStyle.SP_ArrowBack))
        btn_back.setIconSize(QSize(16, 16))
        btn_back.clicked.connect(self.back_requested.emit)

        title = QLabel(self.product["name"])
        title.setObjectName("PageTitle")

        top_lay.addWidget(btn_back)
        top_lay.addSpacing(16)
        top_lay.addWidget(title)
        top_lay.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_lay = QVBoxLayout(content)
        content_lay.setContentsMargins(24, 24, 24, 24)
        content_lay.setSpacing(20)

        top_block = QHBoxLayout()
        top_block.setSpacing(24)

        img_label = QLabel()
        img_label.setObjectName("ProductImageLarge")
        img_label.setFixedSize(400, 340)
        img_label.setAlignment(Qt.AlignCenter)
        pix = self._load_pixmap()
        if pix:
            img_label.setPixmap(pix)
        else:
            img_label.setText("нет фото")
        top_block.addWidget(img_label)

        info = QVBoxLayout()
        info.setSpacing(10)

        brand = QLabel(f"  {self.product.get('brand', '—')}")
        brand.setObjectName("ProductBrandLarge")
        info.addWidget(brand)

        cat_name = self.product_ctrl.get_category_name(self.product["category_id"])
        category = QLabel(f"  {cat_name}")
        category.setObjectName("Hint")
        info.addWidget(category)

        rating_row = QHBoxLayout()
        rating_row.setSpacing(8)
        self.rating_display = StarRatingDisplay(
            self.product.get("rating", 0), size=20
        )
        self.ratings_count_label = QLabel(
            f"({len(self.product.get('ratings', []))} оценок)"
        )
        rating_row.addWidget(self.rating_display)
        rating_row.addWidget(self.ratings_count_label)
        rating_row.addStretch()
        info.addLayout(rating_row)

        price = QLabel(f"{self.product.get('current_price', 0):.2f} ₽")
        price.setObjectName("ProductPriceLarge")
        info.addWidget(price)

        info.addSpacing(10)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.btn_fav = QPushButton(self._fav_text())
        self.btn_fav.setObjectName("FavButton")
        self.btn_fav.setFixedHeight(44)
        self.btn_fav.setMinimumWidth(160)
        self.btn_fav.clicked.connect(self._on_toggle_favorite)

        btn_cart = QPushButton("В корзину")
        btn_cart.setFixedHeight(44)
        btn_cart.setMinimumWidth(160)
        btn_cart.clicked.connect(self._on_add_to_cart)

        self.btn_compare = QPushButton(self._compare_text())
        self.btn_compare.setObjectName("FavButton")
        self.btn_compare.setFixedHeight(44)
        self.btn_compare.setMinimumWidth(160)
        self.btn_compare.clicked.connect(self._on_toggle_compare)

        btn_row.addWidget(self.btn_fav)
        btn_row.addWidget(btn_cart)
        btn_row.addWidget(self.btn_compare)
        btn_row.addStretch()
        info.addLayout(btn_row)

        info.addSpacing(10)
        my_label = QLabel("Ваша оценка:")
        my_label.setObjectName("SectionTitle")
        info.addWidget(my_label)

        self.star_input = StarRatingInput(
            value=self.product_ctrl.get_user_rating(self.product), size=26
        )
        self.star_input.rating_changed.connect(
            lambda v: self._on_rate_from_widget(v, source="top")
        )
        info.addWidget(self.star_input)

        info.addStretch()

        info_widget = QWidget()
        info_widget.setLayout(info)
        info_widget.setMinimumWidth(500)
        top_block.addWidget(info_widget, 1)

        content_lay.addLayout(top_block)

        details = QFrame()
        details.setObjectName("Card")
        d_lay = QVBoxLayout(details)
        d_lay.setContentsMargins(20, 16, 20, 16)
        d_lay.setSpacing(12)

        d_lay.addWidget(self._section("Состав", self.product.get("composition", "—")))

        d_lay.addWidget(self._chips_section(
            "Аллергены",
            self.product.get("allergens", []),
            "#FEE2E2", "#B91C1C"
        ))
        d_lay.addWidget(self._chips_section(
            "Пищевые добавки",
            self.product.get("additives", []),
            "#FEF3C7", "#92400E"
        ))
        content_lay.addWidget(details)

        analysis = self._build_analysis_block()
        content_lay.addWidget(analysis)

        review_form = QFrame()
        review_form.setObjectName("Card")
        rf_lay = QVBoxLayout(review_form)
        rf_lay.setContentsMargins(20, 16, 20, 16)
        rf_lay.setSpacing(10)

        rf_title = QLabel("Оставить отзыв")
        rf_title.setObjectName("SectionTitle")
        rf_lay.addWidget(rf_title)

        rf_lay.addWidget(QLabel("Ваша оценка:"))
        self.new_review_stars = StarRatingInput(size=24)
        self.new_review_stars.rating_changed.connect(
            lambda v: self._on_rate_from_widget(v, source="form")
        )
        rf_lay.addWidget(self.new_review_stars)

        self.review_text = QTextEdit()
        self.review_text.setPlaceholderText("Расскажите о товаре...")
        self.review_text.setFixedHeight(110)
        rf_lay.addWidget(self.review_text)

        btn_send_review = QPushButton("Опубликовать отзыв")
        btn_send_review.setFixedHeight(40)
        btn_send_review.setMaximumWidth(240)
        btn_send_review.clicked.connect(self._on_send_review)
        rf_lay.addWidget(btn_send_review, alignment=Qt.AlignLeft)

        content_lay.addWidget(review_form)

        self.reviews_title = QLabel("Отзывы")
        self.reviews_title.setObjectName("SectionTitle")
        content_lay.addWidget(self.reviews_title)

        self.reviews_container = QVBoxLayout()
        self.reviews_container.setSpacing(12)
        content_lay.addLayout(self.reviews_container)

        content_lay.addStretch()

        scroll.setWidget(content)
        root.addWidget(top)
        root.addWidget(scroll, 1)

    def _sync_star_widgets(self, value: int):
        """Устанавливает одинаковое значение в оба виджета БЕЗ эмита сигналов."""
        self._syncing_rating = True
        try:
            self.star_input.set_value(value)
            self.new_review_stars.set_value(value)
        finally:
            self._syncing_rating = False

    def _on_rate_from_widget(self, value: int, source: str):
        """Единый обработчик клика по звёздам из любого виджета."""
        if self._syncing_rating:
            return

        ok, msg = self.product_ctrl.rate_product(self.product_id, value)
        if not ok:
            QMessageBox.warning(self, "Ошибка", msg)
            return

        self._sync_star_widgets(value)

        self.product = self.product_ctrl.get_product(self.product_id)
        new_avg = self.product.get("rating", 0)
        cnt = len(self.product.get("ratings", []))

        self.rating_display.update_value(new_avg)
        self.ratings_count_label.setText(f"({cnt} оценок)")

    def _section(self, title: str, text: str) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)
        t = QLabel(title)
        t.setObjectName("SectionTitle")
        body = QLabel(text)
        body.setWordWrap(True)
        body.setStyleSheet("color:#334155;")
        lay.addWidget(t)
        lay.addWidget(body)
        return w

    def _chips_section(self, title: str, items: list, bg: str, fg: str) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)
        t = QLabel(title)
        t.setObjectName("SectionTitle")
        lay.addWidget(t)
        chips_row = QHBoxLayout()
        chips_row.setSpacing(6)
        if items:
            for item in items:
                chip = QLabel(item)
                chip.setStyleSheet(
                    f"background:{bg}; color:{fg};"
                    f"border-radius: 10px; padding: 3px 10px;"
                    f"font-size: 12px; font-weight: 600;"
                )
                chips_row.addWidget(chip)
        else:
            none_lbl = QLabel("нет")
            none_lbl.setObjectName("Hint")
            chips_row.addWidget(none_lbl)
        chips_row.addStretch()
        lay.addLayout(chips_row)
        return w

    def _load_pixmap(self) -> QPixmap | None:
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
                    return pix.scaled(
                        400, 340, Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
        return None

    def _fav_text(self) -> str:
        if self.product_ctrl.is_favorite(self.product_id):
            return "⭐  В избранном"
        return "☆  В избранное"

    def _on_toggle_favorite(self):
        ok, msg = self.product_ctrl.toggle_favorite(self.product_id)
        if not ok:
            QMessageBox.warning(self, "Ошибка", msg)
            return
        self.btn_fav.setText(self._fav_text())

    def _on_add_to_cart(self):
        ok, msg = self.product_ctrl.add_to_cart(self.product_id, 1)
        if ok:
            QMessageBox.information(self, "Корзина", msg)
        else:
            QMessageBox.warning(self, "Ошибка", msg)

    def _compare_text(self) -> str:
        if CompareController.is_selected(self.product_id):
            return "В сравнении"
        return "Сравнить"

    def _on_toggle_compare(self):
        ok, msg = CompareController.toggle(self.product_id)
        if not ok:
            QMessageBox.warning(self, "Сравнение", msg)
            return
        self.btn_compare.setText(self._compare_text())

    def _on_send_review(self):
        text = self.review_text.toPlainText().strip()
        rating = self.new_review_stars.value()

        if rating < 1:
            QMessageBox.warning(self, "Ошибка",
                                "Поставьте оценку от 1 до 5 звёзд.")
            return

        ok, msg = self.review_ctrl.add_review(self.product_id, text, rating)
        if not ok:
            QMessageBox.warning(self, "Ошибка", msg)
            return

        QMessageBox.information(self, "Успех", msg)
        self.review_text.clear()

        self.new_review_stars.set_value(0)

        self._load_reviews()

    def _load_reviews(self):
        while self.reviews_container.count():
            item = self.reviews_container.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        reviews = self.review_ctrl.list_reviews(self.product_id)
        self.reviews_title.setText(f"Отзывы ({len(reviews)})")

        if not reviews:
            empty = QLabel("Отзывов пока нет. Будьте первым!")
            empty.setObjectName("Hint")
            empty.setAlignment(Qt.AlignCenter)
            self.reviews_container.addWidget(empty)
            return

        for r in reviews:
            rw = ReviewWidget(r)
            rw.like_clicked.connect(self._on_like)
            rw.dislike_clicked.connect(self._on_dislike)
            rw.comment_added.connect(self._on_comment)
            rw.delete_clicked.connect(self._on_delete_review)
            self.reviews_container.addWidget(rw)

    def _on_like(self, review_id):
        self.review_ctrl.toggle_like(review_id)
        self._load_reviews()

    def _on_dislike(self, review_id):
        self.review_ctrl.toggle_dislike(review_id)
        self._load_reviews()

    def _on_comment(self, review_id, text):
        ok, msg = self.review_ctrl.add_comment(review_id, text)
        if not ok:
            QMessageBox.warning(self, "Ошибка", msg)
            return
        self._load_reviews()

    def _on_delete_review(self, review_id):
        confirm = QMessageBox.question(
            self, "Удаление",
            "Удалить этот отзыв?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return
        ok, msg = self.review_ctrl.delete_review(review_id)
        if not ok:
            QMessageBox.warning(self, "Ошибка", msg)
            return
        self._load_reviews()

    def _build_analysis_block(self) -> QFrame:
        result = analyze_composition(self.product.get("composition", ""))

        block = QFrame()
        block.setObjectName("Card")
        lay = QVBoxLayout(block)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(14)

        header = QHBoxLayout()
        title = QLabel("Анализ состава")
        title.setObjectName("SectionTitle")
        header.addWidget(title)
        header.addStretch()

        badge = QLabel(f"  {result['risk_label']}  ")
        badge.setStyleSheet(
            f"background: {result['risk_color']}1A;"
            f"color: {result['risk_color']};"
            f"border: 1px solid {result['risk_color']}55;"
            f"border-radius: 11px; padding: 3px 12px;"
            f"font-size: 12px; font-weight: 700;"
        )
        header.addWidget(badge)
        lay.addLayout(header)

        additives = result["additives"]
        if additives:
            lay.addWidget(self._analysis_label(
                f"Обнаруженные пищевые добавки ({len(additives)}):"
            ))
            for a in additives:
                lay.addWidget(self._additive_row(a))

        allergens = result["allergens"]
        if allergens:
            lay.addWidget(self._analysis_label(
                f"Возможные аллергены ({len(allergens)}):"
            ))
            row = QHBoxLayout()
            row.setSpacing(6)
            for al in allergens:
                chip = QLabel(al["name"])
                chip.setStyleSheet(
                    "background:#FEE2E2; color:#B91C1C;"
                    "border-radius: 10px; padding: 3px 12px;"
                    "font-size: 12px; font-weight: 600;"
                )
                row.addWidget(chip)
            row.addStretch()
            lay.addLayout(row)

        if not additives and not allergens:
            empty = QLabel(
                "В составе не найдено известных добавок и аллергенов."
            )
            empty.setObjectName("Hint")
            lay.addWidget(empty)

        return block

    def _analysis_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            "color:#475569; font-weight: 600; font-size: 12.5px;"
            "padding-top: 4px;"
        )
        return lbl

    def _additive_row(self, additive: dict) -> QFrame:
        risk = additive["risk"]
        colors = {
            1: ("#ECFDF5", "#047857"),
            2: ("#F0FDF4", "#15803D"),
            3: ("#FEF3C7", "#92400E"),
            4: ("#FEE2E2", "#B91C1C"),
            5: ("#FEE2E2", "#7F1D1D"),
        }
        bg, fg = colors.get(risk, ("#F1F5F9", "#475569"))

        row = QFrame()
        row.setStyleSheet(
            f"QFrame {{ background: {bg}; border-radius: 10px; }}"
        )
        lay = QHBoxLayout(row)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(12)

        code = QLabel(additive["code"])
        code.setStyleSheet(
            f"color: {fg}; font-weight: 800; font-size: 13px;"
        )
        code.setFixedWidth(60)

        info = QVBoxLayout()
        info.setSpacing(1)

        name = QLabel(additive["name"])
        name.setStyleSheet(
            f"color: {fg}; font-weight: 700; font-size: 13px;"
        )
        info.addWidget(name)

        category = QLabel(additive["category"])
        category.setStyleSheet(
            f"color: {fg}; font-size: 11px; opacity: 0.85;"
        )
        info.addWidget(category)

        if additive.get("note"):
            note = QLabel(" " + additive["note"])
            note.setWordWrap(True)
            note.setStyleSheet("color:#64748B; font-size: 11.5px;")
            info.addWidget(note)

        lay.addWidget(code)
        lay.addLayout(info, 1)

        risk_lbl = QLabel(f"риск {risk}/5")
        risk_lbl.setStyleSheet(
            f"color: {fg}; font-weight: 700; font-size: 11px;"
        )
        risk_lbl.setAlignment(Qt.AlignRight | Qt.AlignTop)
        lay.addWidget(risk_lbl)

        return row