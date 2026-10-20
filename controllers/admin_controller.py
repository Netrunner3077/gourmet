from bson import ObjectId
from models.product_model import ProductModel
from models.category_model import CategoryModel
from models.user_model import UserModel
from models.review_model import ReviewModel
from utils.session import Session


class AdminController:
    def __init__(self):
        self.products = ProductModel()
        self.categories = CategoryModel()
        self.users = UserModel()
        self.reviews = ReviewModel()

    def is_admin(self) -> bool:
        user = Session.get_user()
        return bool(user and user.get("is_admin"))

    def list_products(self):
        return self.products.get_all()

    def create_product(self, data: dict) -> tuple[bool, str]:
        try:
            self.products.create(
                name=data["name"],
                category_id=data["category_id"],
                brand=data["brand"],
                composition=data["composition"],
                allergens=data.get("allergens", []),
                additives=data.get("additives", []),
                images=data.get("images", []),
                current_price=data.get("current_price", 0.0),
            )
            return True, "Товар добавлен."
        except Exception as e:
            return False, f"Ошибка: {e}"

    def update_product(self, product_id: ObjectId, data: dict) -> tuple[bool, str]:
        try:
            self.products.update(product_id, data)
            return True, "Товар обновлён."
        except Exception as e:
            return False, f"Ошибка: {e}"

    def delete_product(self, product_id: ObjectId) -> tuple[bool, str]:
        self.products.delete(product_id)
        return True, "Товар удалён."

    def list_categories(self):
        return list(self.categories.get_all())

    def create_category(self, name: str) -> tuple[bool, str]:
        if not name.strip():
            return False, "Название не может быть пустым."
        if self.categories.get_by_name(name):
            return False, "Такая категория уже есть."
        self.categories.create(name)
        return True, "Категория добавлена."

    def update_category(self, category_id: ObjectId, name: str) -> tuple[bool, str]:
        if not name.strip():
            return False, "Название не может быть пустым."
        self.categories.update(category_id, name)
        return True, "Категория обновлена."

    def delete_category(self, category_id: ObjectId) -> tuple[bool, str]:
        self.categories.delete(category_id)
        return True, "Категория удалена."

    def list_users(self):
        return self.users.list_all()

    def toggle_user_block(self, user_id: ObjectId) -> tuple[bool, str]:
        u = self.users.get_by_id(user_id)
        if not u:
            return False, "Пользователь не найден."
        self.users.set_blocked(user_id, not u.get("is_blocked", False))
        return True, "Статус изменён."

    def delete_user(self, user_id: ObjectId) -> tuple[bool, str]:
        if Session.get_user_id() == user_id:
            return False, "Нельзя удалить самого себя."
        self.users.delete(user_id)
        return True, "Пользователь удалён."

    def list_reviews(self):
        reviews = self.reviews.list_all()
        if not reviews:
            return []

        prod_ids = list({r["product_id"] for r in reviews if "product_id" in r})
        products_by_id = {
            p["_id"]: p for p in self.products.get_many_by_ids(prod_ids)
        }

        user_ids = list({r["user_id"] for r in reviews if "user_id" in r})
        users_by_id = {
            u["_id"]: u for u in self.users.get_many_by_ids(user_ids)
        }

        for r in reviews:
            prod = products_by_id.get(r.get("product_id"))
            author = users_by_id.get(r.get("user_id"))
            r["product_name"] = prod["name"] if prod else "—"
            r["author_login"] = author["login"] if author else "—"

        return reviews

    def delete_review(self, review_id: ObjectId) -> tuple[bool, str]:
        self.reviews.delete(review_id)
        return True, "Отзыв удалён."