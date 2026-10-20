from bson import ObjectId
from models.review_model import ReviewModel
from models.user_model import UserModel
from utils.session import Session


class ReviewController:
    def __init__(self):
        self.reviews = ReviewModel()
        self.users = UserModel()

    def add_review(self, product_id: ObjectId, text: str, rating: int) -> tuple[bool, str]:
        user_id = Session.get_user_id()
        if not user_id:
            return False, "Сначала войдите в аккаунт."
        if not text.strip():
            return False, "Текст отзыва не может быть пустым."
        if rating < 1 or rating > 5:
            return False, "Поставьте оценку от 1 до 5 звёзд."

        self.reviews.create(product_id, user_id, text.strip(), rating)
        self.users.increment_stat(user_id, "reviews_count", 1)
        return True, "Отзыв опубликован!"

    def list_reviews(self, product_id: ObjectId) -> list[dict]:
        reviews = self.reviews.get_by_product(product_id)
        if not reviews:
            return []

        author_ids = list({r["user_id"] for r in reviews if "user_id" in r})
        authors = {
            u["_id"]: u for u in self.users.get_many_by_ids(author_ids)
        }

        commenter_ids = set()
        for r in reviews:
            for c in r.get("comments", []):
                if "user_id" in c:
                    commenter_ids.add(c["user_id"])
        commenters = {
            u["_id"]: u
            for u in self.users.get_many_by_ids(list(commenter_ids))
        }

        for r in reviews:
            u = authors.get(r["user_id"])
            r["author_login"] = u["login"] if u else "Удалённый"
            r["author_avatar"] = u.get("avatar") if u else None
            for c in r.get("comments", []):
                cu = commenters.get(c["user_id"])
                c["author_login"] = cu["login"] if cu else "Удалённый"

        return reviews

    def delete_review(self, review_id: ObjectId) -> tuple[bool, str]:
        review = self.reviews.get_by_id(review_id)
        if not review:
            return False, "Отзыв не найден."
        user = Session.get_user()
        if not user:
            return False, "Сначала войдите в аккаунт."
        if review["user_id"] != user["_id"] and not user.get("is_admin"):
            return False, "Нет прав для удаления этого отзыва."
        self.reviews.delete(review_id)
        if review["user_id"] == user["_id"]:
            self.users.increment_stat(user["_id"], "reviews_count", -1)
        return True, "Отзыв удалён."

    def toggle_like(self, review_id: ObjectId) -> tuple[bool, str]:
        user_id = Session.get_user_id()
        if not user_id:
            return False, "Сначала войдите в аккаунт."
        self.reviews.toggle_like(review_id, user_id)
        return True, ""

    def toggle_dislike(self, review_id: ObjectId) -> tuple[bool, str]:
        user_id = Session.get_user_id()
        if not user_id:
            return False, "Сначала войдите в аккаунт."
        self.reviews.toggle_dislike(review_id, user_id)
        return True, ""

    def add_comment(self, review_id: ObjectId, text: str) -> tuple[bool, str]:
        user_id = Session.get_user_id()
        if not user_id:
            return False, "Сначала войдите в аккаунт."
        if not text.strip():
            return False, "Текст комментария пуст."
        self.reviews.add_comment(review_id, user_id, text.strip())
        self.users.increment_stat(user_id, "comments_count", 1)
        return True, "Комментарий добавлен."