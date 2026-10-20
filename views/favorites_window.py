from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QGridLayout, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal

from controllers.product_controller import ProductController
from views.product_card import ProductCard


class FavoritesWindow(QWidget):
    back_requested = pyqtSignal()
    product_selected = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.product_ctrl = ProductController()

        self.setWindowTitle("Гурман — Избранное")
        self.setGeometry(320, 80, 1080, 780)
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

        btn_back = QPushButton("← Назад")
        btn_back.setObjectName("GhostButton")
        btn_back.setFixedHeight(38)
        btn_back.clicked.connect(self.back_requested.emit)

        self.title = QLabel("Избранное")
        self.title.setObjectName("PageTitle")

        top_lay.addWidget(btn_back)
        top_lay.addSpacing(12)
        top_lay.addWidget(self.title)
        top_lay.addStretch()

        root.addWidget(top)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.feed = QWidget()
        self.grid = QGridLayout(self.feed)
        self.grid.setContentsMargins(28, 24, 28, 24)
        self.grid.setSpacing(18)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        scroll.setWidget(self.feed)

        root.addWidget(scroll, 1)

    def _load(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        favorites = self.product_ctrl.list_favorites()
        self.title.setText(f"Избранное ({len(favorites)})")

        if not favorites:
            empty = QLabel(
                "В избранном пока пусто.\n\n"
                "Откройте любой товар и нажмите «☆ В избранное», "
                "чтобы добавить его сюда."
            )
            empty.setObjectName("Hint")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet("padding: 80px; font-size: 14px;")
            self.grid.addWidget(empty, 0, 0, 1, 4)
            return

        columns = 4
        for i, product in enumerate(favorites):
            card = ProductCard(product)
            card.clicked.connect(self._on_card_clicked)
            card.fav_toggled.connect(self._on_fav_toggled)
            card.compare_toggled.connect(self._on_compare_toggled)
            row, col = divmod(i, columns)
            self.grid.addWidget(card, row, col)

    def _on_card_clicked(self, product: dict):
        self.product_selected.emit(product["_id"])

    def _on_fav_toggled(self, product_id):
        ok, _ = self.product_ctrl.toggle_favorite(product_id)
        if ok:
            self._load()

    def _on_compare_toggled(self, product_id):
        from controllers.compare_controller import CompareController
        ok, msg = CompareController.toggle(product_id)
        if not ok:
            QMessageBox.warning(self, "Сравнение", msg)
            return
        for i in range(self.grid.count()):
            w = self.grid.itemAt(i).widget()
            if isinstance(w, ProductCard):
                w.refresh_compare()