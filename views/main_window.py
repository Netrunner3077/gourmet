from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QGridLayout, QFrame, QMessageBox, QStyle
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QIcon

from utils.session import Session
from utils.ui_helpers import add_shadow, make_divider
from models.category_model import CategoryModel
from models.product_model import ProductModel
from controllers.product_controller import ProductController
from controllers.cart_controller import CartController
from controllers.compare_controller import CompareController
from controllers.admin_controller import AdminController
from views.product_card import ProductCard


class NavButton(QPushButton):
    def __init__(self, text: str, standard_icon: QStyle.StandardPixmap, parent=None):
        super().__init__(text, parent)
        self.setObjectName("NavButton")
        self.setCheckable(True)
        self.setFixedHeight(44)
        self.setCursor(Qt.PointingHandCursor)
        
        self._base_text = text
        self.setIcon(self.style().standardIcon(standard_icon))
        self.setIconSize(QSize(18, 18))

    def set_badge(self, n: int):
        if n > 0:
            self.setText(f"  {self._base_text}   ({n})")
        else:
            self.setText(f"  {self._base_text}")


class MainWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.cat_model = CategoryModel()
        self.prod_model = ProductModel()
        self.product_ctrl = ProductController()
        self.cart_ctrl = CartController()
        self.admin_ctrl = AdminController()

        self.current_category_id = None
        self.buttons_by_cat_id = {}

        self.setWindowTitle("Гурман")
        self.setGeometry(200, 60, 1320, 840)
        self._build_ui()
        self._load_categories()
        self._load_products()
        self._refresh_badges()
        self._refresh_avatar()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(240)
        sb = QVBoxLayout(sidebar)
        sb.setContentsMargins(16, 20, 16, 20)
        sb.setSpacing(8)

        brand = QLabel("ГУРМАН")
        brand.setObjectName("BrandTitle")
        sb.addWidget(brand)

        brand_sub = QLabel("Вкус, проверенный людьми")
        brand_sub.setObjectName("BrandSubtitle")
        sb.addWidget(brand_sub)

        sb.addSpacing(20)

        self.nav_home = NavButton("Главная", QStyle.SP_DirHomeIcon)
        self.nav_home.clicked.connect(self._load_products)
        self.nav_home.setChecked(True)

        self.nav_fav = NavButton("Избранное", QStyle.SP_DialogApplyButton)
        self.nav_fav.clicked.connect(self._open_favorites)

        self.nav_cart = NavButton("Корзина", QStyle.SP_DriveHDIcon)
        self.nav_cart.clicked.connect(self._open_cart)

        self.nav_cmp = NavButton("Сравнение", QStyle.SP_FileDialogDetailedView)
        self.nav_cmp.clicked.connect(self._open_compare)

        self.nav_profile = NavButton("Профиль", QStyle.SP_ComputerIcon)
        self.nav_profile.clicked.connect(self._open_profile)

        nav_list = [self.nav_home, self.nav_fav, self.nav_cart, self.nav_cmp, self.nav_profile]

        if self.admin_ctrl.is_admin():
            self.nav_admin = NavButton("Админ-панель", QStyle.SP_FileDialogInfoView)
            self.nav_admin.clicked.connect(self._open_admin)
            nav_list.append(self.nav_admin)

        for b in nav_list:
            sb.addWidget(b)

        sb.addStretch()
        sb.addWidget(make_divider())
        sb.addSpacing(8)

        self.btn_avatar_side = QPushButton()
        self.btn_avatar_side.setObjectName("AvatarButton")
        self.btn_avatar_side.setFixedSize(44, 44)
        self.btn_avatar_side.setCursor(Qt.PointingHandCursor)
        self.btn_avatar_side.setToolTip("Открыть профиль")
        self.btn_avatar_side.clicked.connect(self._open_profile)

        side_user_row = QHBoxLayout()
        side_user_row.setSpacing(10)
        side_user_row.addWidget(self.btn_avatar_side)

        self.side_login = QLabel("—")
        self.side_login.setStyleSheet(
            "font-weight: 700; color: #0F172A; font-size: 13px;"
        )
        self.side_login_sub = QLabel("в сети")
        self.side_login_sub.setObjectName("Hint")

        name_col = QVBoxLayout()
        name_col.setSpacing(0)
        name_col.addWidget(self.side_login)
        name_col.addWidget(self.side_login_sub)
        side_user_row.addLayout(name_col)
        side_user_row.addStretch()

        sb.addLayout(side_user_row)
        sb.addSpacing(8)

        btn_logout = QPushButton("Выйти")
        btn_logout.setObjectName("GhostButton")
        btn_logout.setFixedHeight(34)
        btn_logout.clicked.connect(self._on_logout)
        sb.addWidget(btn_logout)

        root.addWidget(sidebar)

        content = QWidget()
        content_lay = QVBoxLayout(content)
        content_lay.setContentsMargins(0, 0, 0, 0)
        content_lay.setSpacing(0)

        top = QWidget()
        top.setObjectName("TopBar")
        top.setFixedHeight(72)
        top_lay = QHBoxLayout(top)
        top_lay.setContentsMargins(28, 14, 28, 14)
        top_lay.setSpacing(16)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("SearchInput")
        self.search_input.setPlaceholderText("Поиск по названию или бренду...")
        self.search_input.setFixedHeight(44)
        self.search_input.setMinimumWidth(360)

        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)
        self._search_timer.timeout.connect(self._load_products)
        self.search_input.textChanged.connect(lambda: self._search_timer.start())

        top_lay.addWidget(self.search_input, 1)

        content_lay.addWidget(top)

        hero = QFrame()
        hero.setObjectName("Hero")
        hero.setFixedHeight(140)
        hero.setStyleSheet(
            "QFrame#Hero {"
            " border-radius: 20px;"
            " background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
            "   stop:0 #059669, stop:1 #0284C7);"
            "}"
        )
        hero_lay = QVBoxLayout(hero)
        hero_lay.setContentsMargins(28, 22, 28, 22)
        hero_lay.setSpacing(6)

        user = Session.get_user() or {}
        greeting = QLabel(f"Привет, {user.get('login', 'гость')}")
        greeting.setObjectName("HeroTitle")

        sub = QLabel(
            "Найди лучший продукт по отзывам реальных людей — "
            "без маркетинга и рекламы."
        )
        sub.setObjectName("HeroSubtitle")

        hero_lay.addWidget(greeting)
        hero_lay.addWidget(sub)
        hero_lay.addStretch()

        content_lay_wrap = QVBoxLayout()
        content_lay_wrap.setContentsMargins(28, 20, 28, 20)
        content_lay_wrap.setSpacing(18)

        cat_row = QHBoxLayout()
        cat_row.setSpacing(10)

        self.btn_all = QPushButton("Все товары")
        self.btn_all.setObjectName("CategoryChip")
        self.btn_all.setCheckable(True)
        self.btn_all.setChecked(True)
        self.btn_all.clicked.connect(lambda: self._select_category(None))
        cat_row.addWidget(self.btn_all)

        self.categories_container = QWidget()
        self.categories_layout = QHBoxLayout(self.categories_container)
        self.categories_layout.setContentsMargins(0, 0, 0, 0)
        self.categories_layout.setSpacing(10)
        cat_row.addWidget(self.categories_container)
        cat_row.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        feed = QWidget()
        self.feed_grid = QGridLayout(feed)
        self.feed_grid.setContentsMargins(0, 0, 0, 0)
        self.feed_grid.setSpacing(18)
        self.feed_grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        scroll.setWidget(feed)

        content_lay_wrap.addWidget(hero)
        content_lay_wrap.addLayout(cat_row)
        content_lay_wrap.addWidget(scroll, 1)

        content_lay.addLayout(content_lay_wrap, 1)

        add_shadow(hero, blur=32, offset=10, alpha=45)

        root.addWidget(content, 1)

    def _load_categories(self):
        cats = list(self.cat_model.get_all())
        while self.categories_layout.count():
            item = self.categories_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        self.buttons_by_cat_id = {}
        for cat in cats:
            btn = QPushButton(cat["name"])
            btn.setObjectName("CategoryChip")
            btn.setCheckable(True)
            cid = cat["_id"]
            btn.clicked.connect(lambda _, i=cid: self._select_category(i))
            self.categories_layout.addWidget(btn)
            self.buttons_by_cat_id[cid] = btn

    def _select_category(self, category_id):
        self.current_category_id = category_id
        self.btn_all.setChecked(category_id is None)
        for cid, b in self.buttons_by_cat_id.items():
            b.setChecked(cid == category_id)
        self._load_products()

    def _load_products(self):
        while self.feed_grid.count():
            item = self.feed_grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        search = self.search_input.text().strip() or None
        products = self.prod_model.get_all(
            category_id=self.current_category_id,
            search=search
        )

        if not products:
            hint = QLabel("Ничего не найдено")
            hint.setObjectName("Hint")
            hint.setAlignment(Qt.AlignCenter)
            self.feed_grid.addWidget(hint, 0, 0, 1, 4)
            return

        columns = 4
        for i, product in enumerate(products):
            card = ProductCard(product)
            card.clicked.connect(self._on_product_clicked)
            card.fav_toggled.connect(self._on_card_fav)
            card.compare_toggled.connect(self._on_card_compare)
            row, col = divmod(i, columns)
            self.feed_grid.addWidget(card, row, col)

    def _on_card_fav(self, product_id):
        ok, _ = self.product_ctrl.toggle_favorite(product_id)
        if ok:
            for i in range(self.feed_grid.count()):
                w = self.feed_grid.itemAt(i).widget()
                if isinstance(w, ProductCard) and w.product["_id"] == product_id:
                    w.refresh_fav()
                    self._refresh_badges()

    def _on_card_compare(self, product_id):
        ok, msg = CompareController.toggle(product_id)
        if not ok:
            QMessageBox.warning(self, "Сравнение", msg)
            return
        for i in range(self.feed_grid.count()):
            w = self.feed_grid.itemAt(i).widget()
            if isinstance(w, ProductCard) and w.product["_id"] == product_id:
                w.refresh_compare()
        self._refresh_badges()

    def _on_product_clicked(self, product: dict):
        from views.product_window import ProductWindow
        self.product_window = ProductWindow(product["_id"])
        self.product_window.back_requested.connect(self._close_product_window)
        self.product_window.show()
        self.hide()

    def _close_product_window(self):
        if self.product_window:
            self.product_window.close()
            self.product_window = None
        self._load_products()
        self._refresh_badges()
        self.show()

    def _open_cart(self):
        from views.cart_window import CartWindow
        self.cart_window = CartWindow()
        self.cart_window.back_requested.connect(self._close_cart)
        self.cart_window.checkout_requested.connect(self._close_cart)
        self.cart_window.show()
        self.hide()

    def _close_cart(self):
        if self.cart_window:
            self.cart_window.close()
            self.cart_window = None
        self._refresh_badges()
        self.show()

    def _open_favorites(self):
        from views.favorites_window import FavoritesWindow
        self.favorites_window = FavoritesWindow()
        self.favorites_window.back_requested.connect(self._close_favorites)
        self.favorites_window.product_selected.connect(self._open_product_from_favorites)
        self.favorites_window.show()
        self.hide()

    def _close_favorites(self):
        if self.favorites_window:
            self.favorites_window.close()
            self.favorites_window = None
        self._load_products()
        self._refresh_badges()
        self.show()

    def _open_product_from_favorites(self, product_id):
        from views.product_window import ProductWindow
        self.product_window = ProductWindow(product_id)
        self.product_window.back_requested.connect(self._close_product_from_favorites)
        self.product_window.show()

    def _close_product_from_favorites(self):
        if self.product_window:
            self.product_window.close()
            self.product_window = None
        if self.favorites_window:
            self.favorites_window._load()
            self.favorites_window.show()

    def _open_compare(self):
        from views.compare_window import CompareWindow
        self.compare_window = CompareWindow()
        self.compare_window.back_requested.connect(self._close_compare)
        self.compare_window.show()
        self.hide()

    def _close_compare(self):
        if self.compare_window:
            self.compare_window.close()
            self.compare_window = None
        self._load_products()
        self._refresh_badges()
        self.show()

    def _open_profile(self):
        from views.profile_window import ProfileWindow
        self.profile_window = ProfileWindow()
        self.profile_window.back_requested.connect(self._close_profile)
        self.profile_window.logout_requested.connect(self._on_logout)
        self.profile_window.product_selected.connect(self._open_product_from_profile)
        self.profile_window.show()
        self.hide()

    def _close_profile(self):
        if self.profile_window:
            self.profile_window.close()
            self.profile_window = None
        self._refresh_avatar()
        self._refresh_badges()
        self.show()

    def _open_product_from_profile(self, product_id):
        from views.product_window import ProductWindow
        self.product_window = ProductWindow(product_id)
        self.product_window.back_requested.connect(self._close_product_from_profile)
        self.product_window.show()

    def _close_product_from_profile(self):
        if self.product_window:
            self.product_window.close()
            self.product_window = None
        if self.profile_window:
            self.profile_window.show()

    def _refresh_badges(self):
        user_id = Session.get_user_id()
        if user_id:
            favorites_count = len(self.product_ctrl.list_favorites())
        else:
            favorites_count = 0
        self.nav_fav.set_badge(favorites_count)
        self.nav_cart.set_badge(self.cart_ctrl.count())
        self.nav_cmp.set_badge(CompareController.count())

    def _refresh_avatar(self):
        from utils.image_utils import get_avatar_path, make_placeholder_avatar
        user = Session.get_user() or {}
        pix = get_avatar_path(user.get("avatar"), size=44)
        if not pix:
            login = user.get("login", "?")
            pix = make_placeholder_avatar(login[:1] or "?", 44)
        self.btn_avatar_side.setIcon(QIcon(pix))
        self.btn_avatar_side.setIconSize(QSize(44, 44))
        self.side_login.setText(user.get("login", "—"))

    def showEvent(self, event):
        super().showEvent(event)
        if Session.is_authenticated() and not Session.refresh():
            QMessageBox.warning(self, "Сессия", "Ваш аккаунт был заблокирован или удалён.")
            QTimer.singleShot(0, self._on_logout)

    def _on_logout(self):
        from controllers.auth_controller import AuthController
        AuthController().logout()
        self.logout_requested.emit()

    def _open_admin(self):
        from views.admin_window import AdminWindow
        self.admin_window = AdminWindow()
        self.admin_window.back_requested.connect(self._close_admin)
        self.admin_window.show()
        self.hide()

    def _close_admin(self):
        if self.admin_window:
            self.admin_window.close()
            self.admin_window = None
        self._load_categories()
        self._load_products()
        self.show()