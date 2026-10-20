from bson import ObjectId
from models.cart_model import CartModel
from models.product_model import ProductModel
from utils.session import Session


class CartController:
    def __init__(self):
        self.carts = CartModel()
        self.products = ProductModel()

    def _uid(self):
        return Session.get_user_id()

    def get_items(self) -> list[dict]:
        uid = self._uid()
        if not uid:
            return []
        cart = self.carts.get_or_create(uid)
        items = cart.get("items", [])
        if not items:
            return []

        product_ids = [i["product_id"] for i in items]
        products_by_id = {
            p["_id"]: p for p in self.products.get_many_by_ids(product_ids)
        }

        result = []
        for i in items:
            p = products_by_id.get(i["product_id"])
            if not p:
                continue
            qty = int(i.get("quantity", 1))
            price = float(p.get("current_price", 0))
            result.append({
                "product": p,
                "quantity": qty,
                "subtotal": price * qty,
            })
        return result

    def total(self) -> float:
        return sum(i["subtotal"] for i in self.get_items())

    def count(self) -> int:
        uid = self._uid()
        if not uid:
            return 0
        return self.carts.count_total_items(uid)

    def add(self, product_id: ObjectId, quantity: int = 1) -> tuple[bool, str]:
        uid = self._uid()
        if not uid:
            return False, "Не авторизован."
        self.carts.add_item(uid, product_id, quantity)
        return True, "Товар добавлен в корзину."

    def update_quantity(self, product_id: ObjectId, quantity: int) -> tuple[bool, str]:
        uid = self._uid()
        if not uid:
            return False, "Не авторизован."
        if quantity < 1:
            return self.remove(product_id)
        self.carts.set_quantity(uid, product_id, quantity)
        return True, "Количество обновлено."

    def remove(self, product_id: ObjectId) -> tuple[bool, str]:
        uid = self._uid()
        if not uid:
            return False, "Не авторизован."
        self.carts.remove_item(uid, product_id)
        return True, "Товар удалён."

    def clear(self) -> tuple[bool, str]:
        uid = self._uid()
        if not uid:
            return False, "Не авторизован."
        self.carts.clear(uid)
        return True, "Корзина очищена."