from bson import ObjectId
from models.product_model import ProductModel
from models.favorite_model import FavoriteModel
from models.cart_model import CartModel
from models.category_model import CategoryModel
from utils.session import Session


class ProductController:
    def __init__(self):
        self.products = ProductModel()
        self.favorites = FavoriteModel()
        self.carts = CartModel()
        self.categories = CategoryModel()

    def get_product(self, product_id: ObjectId) -> dict | None:
        return self.products.get_by_id(product_id)
    
    def get_products_by_ids(self, product_ids: list[ObjectId]) -> list[dict]:
        return self.products.get_many_by_ids(product_ids)

    def list_products(self, category_id=None, search=None):
        return self.products.get_all(category_id=category_id, search=search)

    def get_category_name(self, category_id: ObjectId) -> str:
        cat = self.categories.get_by_id(category_id)
        return cat["name"] if cat else "—"

    def rate_product(self, product_id: ObjectId, value: int) -> tuple[bool, str]:
        user_id = Session.get_user_id()
        if not user_id:
            return False, "Сначала войдите в аккаунт."
        self.products.add_or_update_rating(product_id, user_id, value)
        return True, "Оценка сохранена."

    def get_user_rating(self, product: dict) -> int:
        user_id = Session.get_user_id()
        for r in product.get("ratings", []):
            if r["user_id"] == user_id:
                return r["value"]
        return 0

    def toggle_favorite(self, product_id: ObjectId) -> tuple[bool, str]:
        user_id = Session.get_user_id()
        if not user_id:
            return False, "Сначала войдите в аккаунт."
        is_now_fav = self.favorites.toggle(user_id, product_id)
        if is_now_fav:
            return True, "Добавлено в избранное"
        return True, "Удалено из избранного"

    def is_favorite(self, product_id: ObjectId) -> bool:
        user_id = Session.get_user_id()
        if not user_id:
            return False
        return self.favorites.is_favorite(user_id, product_id)

    def list_favorites(self) -> list[dict]:
        """Возвращает список товаров, добавленных в избранное."""
        user_id = Session.get_user_id()
        if not user_id:
            return []
        product_ids = self.favorites.get_user_products(user_id)
        if not product_ids:
            return []
        return self.products.get_many_by_ids(product_ids)

    def add_to_cart(self, product_id: ObjectId, quantity: int = 1) -> tuple[bool, str]:
        user_id = Session.get_user_id()
        if not user_id:
            return False, "Сначала войдите в аккаунт."
        self.carts.add_item(user_id, product_id, quantity)
        return True, "Товар добавлен в корзину"

    def remove_from_cart(self, product_id: ObjectId) -> tuple[bool, str]:
        user_id = Session.get_user_id()
        if not user_id:
            return False, "Сначала войдите в аккаунт."
        self.carts.remove_item(user_id, product_id)
        return True, "Товар удалён из корзины"