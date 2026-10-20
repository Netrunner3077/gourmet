from bson import ObjectId
from utils.session import Session
from models.user_model import UserModel
from models.review_model import ReviewModel
from models.product_model import ProductModel
from models.favorite_model import FavoriteModel

from utils.image_utils import save_avatar
from utils.validators import validate_password
from utils.security import hash_password, verify_password


class ProfileController:
    def __init__(self):
        self.users = UserModel()
        self.favorites = FavoriteModel()
        self.reviews = ReviewModel()
        self.products = ProductModel()

    def get_current_user(self) -> dict | None:
        uid = Session.get_user_id()
        if not uid:
            return None
        return self.users.get_by_id(uid)

    def reload_session_user(self):
        user = self.get_current_user()
        if user:
            Session.set_user(user)

    def update_avatar(self, source_path: str) -> tuple[bool, str]:
        uid = Session.get_user_id()
        if not uid:
            return False, "Не авторизован."
        dest = save_avatar(uid, source_path)
        if not dest:
            return False, "Не удалось сохранить изображение."
        self.users.update_avatar(uid, dest)
        self.reload_session_user()
        return True, "Аватар обновлён."

    def change_password(self, old_password: str, new_password: str, new_password2: str) -> tuple[bool, str]:
        uid = Session.get_user_id()
        if not uid:
            return False, "Не авторизован."
        user = self.users.get_by_id(uid)
        if not user:
            return False, "Пользователь не найден."

        if not verify_password(old_password, user["password_hash"]):
            return False, "Старый пароль введён неверно."

        if new_password != new_password2:
            return False, "Новые пароли не совпадают."

        ok, msg = validate_password(new_password)
        if not ok:
            return False, msg

        if verify_password(new_password, user["password_hash"]):
            return False, "Новый пароль совпадает со старым."

        self.users.update_password(uid, hash_password(new_password))
        return True, "Пароль успешно изменён."

    def get_stats(self) -> dict:
        uid = Session.get_user_id()
        if not uid:
            return {"reviews": 0, "comments": 0, "favorites": 0}
        return {
            "reviews": self.reviews.count_by_user(uid),
            "comments": self.reviews.count_comments_by_user(uid),
            "favorites": self.favorites.count_by_user(uid),
        }

    def get_favorites(self) -> list[dict]:
        uid = Session.get_user_id()
        if not uid:
            return []
        product_ids = self.favorites.get_user_products(uid)
        if not product_ids:
            return []
        return self.products.get_many_by_ids(product_ids)

    def get_my_reviews(self) -> list[dict]:
        uid = Session.get_user_id()
        if not uid:
            return []
        reviews = self.reviews.get_by_user(uid)
        if not reviews:
            return []

        prod_ids = list({r["product_id"] for r in reviews if "product_id" in r})
        products_by_id = {
            p["_id"]: p for p in self.products.get_many_by_ids(prod_ids)
        }

        commenter_ids = set()
        for r in reviews:
            for c in r.get("comments", []):
                if "user_id" in c:
                    commenter_ids.add(c["user_id"])
        commenters = {
            u["_id"]: u["login"]
            for u in self.users.get_many_by_ids(list(commenter_ids))
        }

        my_login = (self.users.get_by_id(uid) or {}).get("login", "Вы")

        for r in reviews:
            prod = products_by_id.get(r.get("product_id"))
            r["product_name"] = prod["name"] if prod else "Товар удалён"
            r["author_login"] = my_login
            for c in r.get("comments", []):
                c["author_login"] = commenters.get(
                    c.get("user_id"), "Удалённый"
                )
        return reviews