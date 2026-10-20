from bson import ObjectId
from models.database import Database
from utils.time_utils import utcnow


class FavoriteModel:
    def __init__(self):
        self.collection = Database().favorites

    def add(self, user_id: ObjectId, product_id: ObjectId):
        if not self.collection.find_one(
            {"user_id": user_id, "product_id": product_id}
        ):
            self.collection.insert_one({
                "user_id": user_id,
                "product_id": product_id,
                "added_at": utcnow(),
            })

    def remove(self, user_id: ObjectId, product_id: ObjectId):
        self.collection.delete_one(
            {"user_id": user_id, "product_id": product_id}
        )

    def toggle(self, user_id: ObjectId, product_id: ObjectId) -> bool:
        existing = self.collection.find_one(
            {"user_id": user_id, "product_id": product_id}
        )
        if existing:
            self.remove(user_id, product_id)
            return False
        self.add(user_id, product_id)
        return True

    def get_user_products(self, user_id: ObjectId):
        return [
            doc["product_id"]
            for doc in self.collection.find({"user_id": user_id})
        ]

    def count_by_user(self, user_id: ObjectId) -> int:
        return self.collection.count_documents({"user_id": user_id})

    def is_favorite(self, user_id: ObjectId, product_id: ObjectId) -> bool:
        return self.collection.find_one(
            {"user_id": user_id, "product_id": product_id}
        ) is not None