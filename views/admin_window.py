from bson import ObjectId
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QSize
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QLineEdit, QTextEdit, QComboBox,
    QDoubleSpinBox, QDialogButtonBox, QMessageBox, QAbstractItemView,
    QListWidget, QListWidgetItem, QProgressBar, QCheckBox, QStyle
)

from controllers.admin_controller import AdminController
from controllers.import_controller import ImportController


class ProductDialog(QDialog):
    def __init__(self, categories, product=None, parent=None):
        super().__init__(parent)
        self.categories = categories
        self.product = product
        self.result_data = None

        self.setWindowTitle("Редактировать товар" if product else "Новый товар")
        self.setMinimumWidth(520)
        self._build_ui()
        if product:
            self._fill(product)

    def _build_ui(self):
        root = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(10)

        self.name = QLineEdit()
        self.brand = QLineEdit()
        self.category = QComboBox()
        for c in self.categories:
            self.category.addItem(c["name"], c["_id"])
        self.composition = QTextEdit()
        self.composition.setFixedHeight(90)
        self.allergens = QLineEdit()
        self.allergens.setPlaceholderText("через запятую")
        self.additives = QLineEdit()
        self.additives.setPlaceholderText("через запятую")
        self.images = QLineEdit()
        self.images.setPlaceholderText("milk.jpg")
        self.price = QDoubleSpinBox()
        self.price.setRange(0, 100000)
        self.price.setSuffix(" ₽")
        self.price.setDecimals(2)

        form.addRow("Название:", self.name)
        form.addRow("Бренд:", self.brand)
        form.addRow("Категория:", self.category)
        form.addRow("Состав:", self.composition)
        form.addRow("Аллергены:", self.allergens)
        form.addRow("Добавки:", self.additives)
        form.addRow("Файл фото:", self.images)
        form.addRow("Цена:", self.price)

        root.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self._on_ok)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    def _fill(self, p):
        self.name.setText(p.get("name", ""))
        self.brand.setText(p.get("brand", ""))
        idx = self.category.findData(p.get("category_id"))
        if idx >= 0:
            self.category.setCurrentIndex(idx)
        self.composition.setPlainText(p.get("composition", ""))
        self.allergens.setText(", ".join(p.get("allergens", [])))
        self.additives.setText(", ".join(p.get("additives", [])))
        self.images.setText(", ".join(p.get("images", [])))
        self.price.setValue(float(p.get("current_price", 0)))

    def _on_ok(self):
        if not self.name.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите название.")
            return
        self.result_data = {
            "name": self.name.text().strip(),
            "brand": self.brand.text().strip(),
            "category_id": self.category.currentData(),
            "composition": self.composition.toPlainText().strip(),
            "allergens": [x.strip() for x in self.allergens.text().split(",") if x.strip()],
            "additives": [x.strip() for x in self.additives.text().split(",") if x.strip()],
            "images": [x.strip() for x in self.images.text().split(",") if x.strip()],
            "current_price": self.price.value(),
        }
        self.accept()


class CategoryDialog(QDialog):
    def __init__(self, category=None, parent=None):
        super().__init__(parent)
        self.category = category
        self.result_name = None

        self.setWindowTitle("Редактировать категорию" if category else "Новая категория")
        self.setMinimumWidth(320)

        lay = QVBoxLayout(self)
        form = QFormLayout()
        self.name = QLineEdit()
        if category:
            self.name.setText(category.get("name", ""))
        form.addRow("Название:", self.name)
        lay.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_ok)
        buttons.rejected.connect(self.reject)
        lay.addWidget(buttons)

    def _on_ok(self):
        if not self.name.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите название.")
            return
        self.result_name = self.name.text().strip()
        self.accept()


class SearchWorker(QThread):
    finished_ok = pyqtSignal(list)
    failed = pyqtSignal(str)

    def __init__(self, query: str, ctrl: ImportController):
        super().__init__()
        self.query = query
        self.ctrl = ctrl

    def run(self):
        try:
            results = self.ctrl.search(self.query)
            self.finished_ok.emit(results)
        except Exception as e:
            self.failed.emit(str(e))


class ImportWorker(QThread):
    progress = pyqtSignal(str)
    finished_ok = pyqtSignal(int, int)
    failed = pyqtSignal(str)

    def __init__(self, items: list, ctrl: ImportController, default_price: float, download_images: bool):
        super().__init__()
        self.items = items
        self.ctrl = ctrl
        self.default_price = default_price
        self.download_images = download_images

    def run(self):
        ok_count = 0
        fail_count = 0
        for remote in self.items:
            self.progress.emit(f"Импорт: {remote.get('name', '?')}")
            cat_id = self.ctrl.guess_category_id(remote)
            if not cat_id:
                fail_count += 1
                continue
            ok, _ = self.ctrl.import_product(
                remote, cat_id,
                price=self.default_price,
                download_image=self.download_images,
            )
            if ok:
                ok_count += 1
            else:
                fail_count += 1
        self.finished_ok.emit(ok_count, fail_count)


class AdminWindow(QWidget):
    back_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ctrl = AdminController()
        self.import_ctrl = ImportController()

        self.setWindowTitle("Гурман — Админ-панель")
        self.setGeometry(200, 60, 1240, 820)
        self._build_ui()
        self._load_all()

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

        title = QLabel("Админ-панель")
        title.setObjectName("PageTitle")

        top_lay.addWidget(btn_back)
        top_lay.addSpacing(12)
        top_lay.addWidget(title)
        top_lay.addStretch()

        root.addWidget(top)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background: transparent; }
            QTabBar::tab {
                background: transparent; color: #475569;
                padding: 10px 22px; margin-right: 4px;
                border-radius: 8px; font-weight: 600;
            }
            QTabBar::tab:selected { background: #ECFDF5; color: #047857; }
            QTabBar::tab:hover:!selected { background: #F1F5F9; }
        """)

        self.tabs.addTab(self._build_products_tab(), "Товары")
        self.tabs.addTab(self._build_categories_tab(), "Категории")
        self.tabs.addTab(self._build_users_tab(), "Пользователи")
        self.tabs.addTab(self._build_reviews_tab(), "Отзывы")
        self.tabs.addTab(self._build_import_tab(), "Импорт")

        root.addWidget(self.tabs, 1)

    def _build_products_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        bar = QHBoxLayout()
        btn_add = QPushButton("Добавить товар")
        btn_add.setFixedHeight(38)
        btn_add.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        btn_add.setIconSize(QSize(16, 16))
        btn_add.clicked.connect(self._on_add_product)
        
        btn_edit = QPushButton("Редактировать")
        btn_edit.setObjectName("GhostButton")
        btn_edit.setFixedHeight(38)
        btn_edit.clicked.connect(self._on_edit_product)
        
        btn_del = QPushButton("Удалить")
        btn_del.setObjectName("GhostButton")
        btn_del.setFixedHeight(38)
        btn_del.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        btn_del.setIconSize(QSize(16, 16))
        btn_del.clicked.connect(self._on_delete_product)

        bar.addWidget(btn_add)
        bar.addWidget(btn_edit)
        bar.addWidget(btn_del)
        bar.addStretch()
        lay.addLayout(bar)

        self.products_table = QTableWidget()
        self.products_table.setColumnCount(5)
        self.products_table.setHorizontalHeaderLabels(["Название", "Бренд", "Категория", "Цена", "Рейтинг"])
        self.products_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.products_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.products_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.products_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.products_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.products_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.products_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.products_table.verticalHeader().setVisible(False)
        self.products_table.setAlternatingRowColors(True)

        lay.addWidget(self.products_table)
        return w

    def _build_categories_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        bar = QHBoxLayout()
        btn_add = QPushButton("+  Добавить категорию")
        btn_add.setFixedHeight(38)
        btn_add.clicked.connect(self._on_add_category)
        btn_edit = QPushButton("Переименовать")
        btn_edit.setObjectName("GhostButton")
        btn_edit.setFixedHeight(38)
        btn_edit.clicked.connect(self._on_edit_category)
        btn_del = QPushButton("Удалить")
        btn_del.setObjectName("GhostButton")
        btn_del.setFixedHeight(38)
        btn_del.clicked.connect(self._on_delete_category)

        bar.addWidget(btn_add)
        bar.addWidget(btn_edit)
        bar.addWidget(btn_del)
        bar.addStretch()
        lay.addLayout(bar)

        self.categories_table = QTableWidget()
        self.categories_table.setColumnCount(2)
        self.categories_table.setHorizontalHeaderLabels(["Название", "Товаров"])
        self.categories_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.Stretch
        )
        self.categories_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeToContents
        )
        self.categories_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.categories_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.categories_table.verticalHeader().setVisible(False)
        self.categories_table.setAlternatingRowColors(True)

        lay.addWidget(self.categories_table)
        return w

    def _build_users_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        bar = QHBoxLayout()
        btn_block = QPushButton("Блок / Разблок")
        btn_block.setFixedHeight(38)
        btn_block.clicked.connect(self._on_toggle_block)
        btn_del = QPushButton("Удалить")
        btn_del.setObjectName("GhostButton")
        btn_del.setFixedHeight(38)
        btn_del.clicked.connect(self._on_delete_user)

        bar.addWidget(btn_block)
        bar.addWidget(btn_del)
        bar.addStretch()
        lay.addLayout(bar)

        self.users_table = QTableWidget()
        self.users_table.setColumnCount(5)
        self.users_table.setHorizontalHeaderLabels(
            ["Логин", "Регистрация", "Отзывы", "Комментарии", "Статус"]
        )
        self.users_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.Stretch
        )
        for i in range(1, 5):
            self.users_table.horizontalHeader().setSectionResizeMode(
                i, QHeaderView.ResizeToContents
            )
        self.users_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.users_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.users_table.verticalHeader().setVisible(False)
        self.users_table.setAlternatingRowColors(True)

        lay.addWidget(self.users_table)
        return w

    def _build_reviews_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        bar = QHBoxLayout()
        btn_del = QPushButton("Удалить отзыв")
        btn_del.setFixedHeight(38)
        btn_del.clicked.connect(self._on_delete_review)
        bar.addWidget(btn_del)
        bar.addStretch()
        lay.addLayout(bar)

        self.reviews_table = QTableWidget()
        self.reviews_table.setColumnCount(5)
        self.reviews_table.setHorizontalHeaderLabels(
            ["Товар", "Автор", "Оценка", "Лайки", "Текст"]
        )
        self.reviews_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents
        )
        self.reviews_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeToContents
        )
        self.reviews_table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeToContents
        )
        self.reviews_table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeToContents
        )
        self.reviews_table.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.Stretch
        )
        self.reviews_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.reviews_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.reviews_table.verticalHeader().setVisible(False)
        self.reviews_table.setAlternatingRowColors(True)

        lay.addWidget(self.reviews_table)
        return w

    def _load_all(self):
        self._load_products()
        self._load_categories()
        self._load_users()
        self._load_reviews()

    def _load_products(self):
        products = self.ctrl.list_products()
        cats = {c["_id"]: c["name"] for c in self.ctrl.list_categories()}

        self.products_table.setRowCount(len(products))
        self._product_ids = []
        for row, p in enumerate(products):
            self._product_ids.append(p["_id"])
            vals = [
                p.get("name", ""),
                p.get("brand", ""),
                cats.get(p.get("category_id"), "—"),
                f"{p.get('current_price', 0):.2f} ₽",
                f"{p.get('rating', 0):.2f}",
            ]
            for col, v in enumerate(vals):
                self.products_table.setItem(row, col, QTableWidgetItem(str(v)))

    def _load_categories(self):
        cats = self.ctrl.list_categories()
        products = self.ctrl.list_products()
        counts = {}
        for p in products:
            counts[p.get("category_id")] = counts.get(p.get("category_id"), 0) + 1

        self.categories_table.setRowCount(len(cats))
        self._category_ids = []
        for row, c in enumerate(cats):
            self._category_ids.append(c["_id"])
            self.categories_table.setItem(row, 0, QTableWidgetItem(c["name"]))
            self.categories_table.setItem(
                row, 1, QTableWidgetItem(str(counts.get(c["_id"], 0)))
            )

    def _load_users(self):
        users = self.ctrl.list_users()
        self.users_table.setRowCount(len(users))
        self._user_ids = []
        for row, u in enumerate(users):
            self._user_ids.append(u["_id"])
            stats = u.get("stats", {})
            status = "заблокирован" if u.get("is_blocked") else "активен"
            if u.get("is_admin"):
                status += " · admin"
            created = u.get("created_at")
            created_str = created.strftime("%d.%m.%Y") if created else "—"
            vals = [
                u.get("login", ""),
                created_str,
                str(stats.get("reviews_count", 0)),
                str(stats.get("comments_count", 0)),
                status,
            ]
            for col, v in enumerate(vals):
                self.users_table.setItem(row, col, QTableWidgetItem(v))

    def _load_reviews(self):
        reviews = self.ctrl.list_reviews()
        self.reviews_table.setRowCount(len(reviews))
        self._review_ids = []
        for row, r in enumerate(reviews):
            self._review_ids.append(r["_id"])
            text = r.get("text", "")
            if len(text) > 80:
                text = text[:77] + "…"
            vals = [
                r.get("product_name", "—"),
                r.get("author_login", "—"),
                "★" * r.get("rating", 0),
                str(r.get("likes", 0)),
                text,
            ]
            for col, v in enumerate(vals):
                self.reviews_table.setItem(row, col, QTableWidgetItem(str(v)))

    def _selected_product_id(self):
        rows = self.products_table.selectionModel().selectedRows()
        if not rows:
            return None
        return self._product_ids[rows[0].row()]

    def _selected_category_id(self):
        rows = self.categories_table.selectionModel().selectedRows()
        if not rows:
            return None
        return self._category_ids[rows[0].row()]

    def _selected_user_id(self):
        rows = self.users_table.selectionModel().selectedRows()
        if not rows:
            return None
        return self._user_ids[rows[0].row()]

    def _selected_review_id(self):
        rows = self.reviews_table.selectionModel().selectedRows()
        if not rows:
            return None
        return self._review_ids[rows[0].row()]

    def _on_add_product(self):
        cats = self.ctrl.list_categories()
        if not cats:
            QMessageBox.warning(self, "Ошибка", "Сначала создайте категорию.")
            return
        dlg = ProductDialog(cats, parent=self)
        if dlg.exec_() == QDialog.Accepted:
            ok, msg = self.ctrl.create_product(dlg.result_data)
            if ok:
                self._load_products()
            else:
                QMessageBox.warning(self, "Ошибка", msg)

    def _on_edit_product(self):
        pid = self._selected_product_id()
        if not pid:
            QMessageBox.information(self, "Товар", "Выберите товар.")
            return
        product = self.ctrl.products.get_by_id(pid)
        cats = self.ctrl.list_categories()
        dlg = ProductDialog(cats, product=product, parent=self)
        if dlg.exec_() == QDialog.Accepted:
            ok, msg = self.ctrl.update_product(pid, dlg.result_data)
            if ok:
                self._load_products()
            else:
                QMessageBox.warning(self, "Ошибка", msg)

    def _on_delete_product(self):
        pid = self._selected_product_id()
        if not pid:
            QMessageBox.information(self, "Товар", "Выберите товар.")
            return
        if QMessageBox.question(
            self, "Удаление", "Удалить этот товар?",
            QMessageBox.Yes | QMessageBox.No
        ) != QMessageBox.Yes:
            return
        ok, msg = self.ctrl.delete_product(pid)
        if ok:
            self._load_products()

    def _on_add_category(self):
        dlg = CategoryDialog(parent=self)
        if dlg.exec_() == QDialog.Accepted:
            ok, msg = self.ctrl.create_category(dlg.result_name)
            if ok:
                self._load_categories()
            else:
                QMessageBox.warning(self, "Ошибка", msg)

    def _on_edit_category(self):
        cid = self._selected_category_id()
        if not cid:
            QMessageBox.information(self, "Категория", "Выберите категорию.")
            return
        cat = self.ctrl.categories.get_by_id(cid)
        dlg = CategoryDialog(category=cat, parent=self)
        if dlg.exec_() == QDialog.Accepted:
            ok, msg = self.ctrl.update_category(cid, dlg.result_name)
            if ok:
                self._load_categories()
            else:
                QMessageBox.warning(self, "Ошибка", msg)

    def _on_delete_category(self):
        cid = self._selected_category_id()
        if not cid:
            QMessageBox.information(self, "Категория", "Выберите категорию.")
            return
        if QMessageBox.question(
            self, "Удаление",
            "Удалить категорию? Товары в ней останутся без категории.",
            QMessageBox.Yes | QMessageBox.No
        ) != QMessageBox.Yes:
            return
        ok, msg = self.ctrl.delete_category(cid)
        if ok:
            self._load_categories()

    def _on_toggle_block(self):
        uid = self._selected_user_id()
        if not uid:
            QMessageBox.information(self, "Пользователь", "Выберите пользователя.")
            return
        ok, msg = self.ctrl.toggle_user_block(uid)
        if ok:
            self._load_users()
        else:
            QMessageBox.warning(self, "Ошибка", msg)

    def _on_delete_user(self):
        uid = self._selected_user_id()
        if not uid:
            QMessageBox.information(self, "Пользователь", "Выберите пользователя.")
            return
        if QMessageBox.question(
            self, "Удаление", "Удалить пользователя?",
            QMessageBox.Yes | QMessageBox.No
        ) != QMessageBox.Yes:
            return
        ok, msg = self.ctrl.delete_user(uid)
        if ok:
            self._load_users()
        else:
            QMessageBox.warning(self, "Ошибка", msg)

    def _on_delete_review(self):
        rid = self._selected_review_id()
        if not rid:
            QMessageBox.information(self, "Отзыв", "Выберите отзыв.")
            return
        if QMessageBox.question(
            self, "Удаление", "Удалить отзыв?",
            QMessageBox.Yes | QMessageBox.No
        ) != QMessageBox.Yes:
            return
        ok, msg = self.ctrl.delete_review(rid)
        if ok:
            self._load_reviews()

    def _build_import_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        info = QLabel(
            "Источник: OpenFoodFacts (открытая база продуктов). "
            "Найдите товары по названию или штрихкоду, отметьте нужные "
            "и нажмите «Импортировать»."
        )
        info.setWordWrap(True)
        info.setObjectName("Hint")
        lay.addWidget(info)

        search_bar = QHBoxLayout()
        search_bar.setSpacing(10)

        self.import_search_input = QLineEdit()
        self.import_search_input.setPlaceholderText(
            "Например: молоко, сыр российский, кола"
        )
        self.import_search_input.returnPressed.connect(self._on_import_search)

        self.import_barcode_input = QLineEdit()
        self.import_barcode_input.setPlaceholderText("или штрихкод")
        self.import_barcode_input.setFixedWidth(180)
        self.import_barcode_input.returnPressed.connect(self._on_import_barcode)

        self.btn_search = QPushButton("Найти")
        self.btn_search.setFixedHeight(38)
        self.btn_search.clicked.connect(self._on_import_search)

        self.btn_barcode = QPushButton("По штрихкоду")
        self.btn_barcode.setObjectName("GhostButton")
        self.btn_barcode.setFixedHeight(38)
        self.btn_barcode.clicked.connect(self._on_import_barcode)

        search_bar.addWidget(self.import_search_input, 1)
        search_bar.addWidget(self.import_barcode_input)
        search_bar.addWidget(self.btn_search)
        search_bar.addWidget(self.btn_barcode)
        lay.addLayout(search_bar)

        self.import_status = QLabel("Готово к поиску.")
        self.import_status.setObjectName("Hint")
        lay.addWidget(self.import_status)

        self.import_progress = QProgressBar()
        self.import_progress.setFixedHeight(6)
        self.import_progress.setTextVisible(False)
        self.import_progress.setVisible(False)
        self.import_progress.setStyleSheet(
            "QProgressBar { background: #E2E8F0; border: none;"
            " border-radius: 3px; }"
            "QProgressBar::chunk { background: #059669;"
            " border-radius: 3px; }"
        )
        lay.addWidget(self.import_progress)

        self.import_list = QListWidget()
        self.import_list.setStyleSheet(
            "QListWidget { background: #FFFFFF; border: 1px solid #E2E8F0;"
            " border-radius: 12px; padding: 8px; }"
            "QListWidget::item { padding: 8px; border-radius: 8px; }"
            "QListWidget::item:selected { background: #ECFDF5;"
            " color: #047857; }"
            "QListWidget::item:hover { background: #F1F5F9; }"
        )
        self.import_list.setSelectionMode(QListWidget.MultiSelection)
        lay.addWidget(self.import_list, 1)

        options = QHBoxLayout()
        options.setSpacing(14)

        price_lbl = QLabel("Цена по умолчанию:")
        options.addWidget(price_lbl)

        self.import_default_price = QDoubleSpinBox()
        self.import_default_price.setRange(0, 100000)
        self.import_default_price.setDecimals(2)
        self.import_default_price.setSuffix(" ₽")
        self.import_default_price.setValue(0.0)
        options.addWidget(self.import_default_price)

        self.import_download_images = QCheckBox("Скачивать изображения")
        self.import_download_images.setChecked(True)
        options.addWidget(self.import_download_images)

        options.addStretch()

        self.btn_import = QPushButton("⬇  Импортировать выбранные")
        self.btn_import.setFixedHeight(38)
        self.btn_import.setEnabled(False)
        self.btn_import.clicked.connect(self._on_import_selected)
        options.addWidget(self.btn_import)

        lay.addLayout(options)

        self._import_results = []
        return w

    def _on_import_search(self):
        query = self.import_search_input.text().strip()
        if not query:
            self.import_status.setText("Введите запрос.")
            return
        self._run_search(query)

    def _on_import_barcode(self):
        barcode = self.import_barcode_input.text().strip()
        if not barcode:
            self.import_status.setText("Введите штрихкод.")
            return
        self._run_search(barcode, by_barcode=True)

    def _run_search(self, query, by_barcode=False):
        self.import_status.setText("Поиск...")
        self.import_list.clear()
        self._import_results = []
        self.btn_search.setEnabled(False)
        self.btn_barcode.setEnabled(False)
        self.btn_import.setEnabled(False)

        if by_barcode:
            try:
                result = self.import_ctrl.get_by_barcode(query)
            except Exception as e:
                self.import_status.setText(f"Ошибка: {e}")
                self.btn_search.setEnabled(True)
                self.btn_barcode.setEnabled(True)
                return
            self._on_search_done([result] if result else [])
        else:
            self._search_worker = SearchWorker(query, self.import_ctrl)
            self._search_worker.finished_ok.connect(self._on_search_done)
            self._search_worker.failed.connect(self._on_search_error)
            self._search_worker.start()

    def _on_search_done(self, results):
        self.btn_search.setEnabled(True)
        self.btn_barcode.setEnabled(True)

        self.import_list.clear()
        self._import_results = results

        if not results:
            self.import_status.setText("Ничего не найдено.")
            return

        for r in results:
            name = r.get("name", "—")
            brand = r.get("brand", "—")
            barcode = r.get("barcode", "")
            text = f"{name}  ·  {brand}"
            if barcode:
                text += f"  ·  {barcode}"

            item = QListWidgetItem(text)
            item.setData(0x0100, r)
            self.import_list.addItem(item)

        self.import_status.setText(
            f"Найдено: {len(results)}. Выделите нужные и нажмите «Импортировать»."
        )
        self.btn_import.setEnabled(True)

    def _on_search_error(self, msg):
        self.btn_search.setEnabled(True)
        self.btn_barcode.setEnabled(True)
        self.import_status.setText(f"Ошибка поиска: {msg}")

    def _on_import_selected(self):
        items = self.import_list.selectedItems()
        if not items:
            QMessageBox.information(self, "Импорт", "Не выбрано ни одного товара.")
            return

        selected = [it.data(0x0100) for it in items]
        price = self.import_default_price.value()
        download = self.import_download_images.isChecked()

        self.btn_import.setEnabled(False)
        self.btn_search.setEnabled(False)
        self.btn_barcode.setEnabled(False)
        self.import_progress.setVisible(True)
        self.import_progress.setRange(0, len(selected))
        self.import_progress.setValue(0)

        self._import_worker = ImportWorker(
            selected, self.import_ctrl, price, download
        )
        self._import_worker.progress.connect(self._on_import_progress)
        self._import_worker.finished_ok.connect(self._on_import_done)
        self._import_worker.failed.connect(self._on_import_error)
        self._import_worker.start()

    def _on_import_progress(self, text):
        self.import_status.setText(text)
        self.import_progress.setValue(self.import_progress.value() + 1)

    def _on_import_done(self, ok_count, fail_count):
        self.import_progress.setVisible(False)
        self.btn_search.setEnabled(True)
        self.btn_barcode.setEnabled(True)
        self.btn_import.setEnabled(True)

        self._load_products()
        self._load_categories()

        QMessageBox.information(
            self, "Импорт завершён",
            f"Успешно: {ok_count}\nПропущено/ошибок: {fail_count}"
        )
        self.import_status.setText(
            f"Импорт завершён. Успешно: {ok_count}, ошибок: {fail_count}."
        )

    def _on_import_error(self, msg):
        self.import_progress.setVisible(False)
        self.btn_search.setEnabled(True)
        self.btn_barcode.setEnabled(True)
        self.btn_import.setEnabled(True)
        self.import_status.setText(f"Ошибка импорта: {msg}")