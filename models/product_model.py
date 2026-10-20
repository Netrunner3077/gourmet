import re
from bson import ObjectId
from models.database import Database
from utils.time_utils import utcnow


class ProductModel:
    def __init__(self):
        self.collection = Database().products

    def create(self, name, category_id, brand, composition, allergens=None, additives=None, images=None, current_price=0.0):
        doc = {
            "name": name,
            "category_id": category_id,
            "brand": brand,
            "composition": composition,
            "allergens": allergens or [],
            "additives": additives or [],
            "images": images or [],
            "current_price": float(current_price),
            "rating": 0.0,
            "ratings": [],
            "created_at": utcnow(),
        }
        return self.collection.insert_one(doc).inserted_id

    def get_all(self, category_id=None, search=None, sort="name"):
        query = {}
        if category_id:
            query["category_id"] = category_id
        if search:
            safe = re.escape(search)
            query["$or"] = [
                {"name": {"$regex": safe, "$options": "i"}},
                {"brand": {"$regex": safe, "$options": "i"}},
            ]
        return list(self.collection.find(query).sort(sort, 1))

    def get_by_id(self, product_id: ObjectId):
        return self.collection.find_one({"_id": product_id})

    def find_by_name(self, name: str):
        return self.collection.find_one({"name": name})

    def get_many_by_ids(self, ids: list[ObjectId]):
        if not ids:
            return []
        return list(self.collection.find({"_id": {"$in": ids}}))

    def add_or_update_rating(self, product_id: ObjectId, user_id: ObjectId, value: int):
        value = max(1, min(5, int(value)))
        self.collection.update_one(
            {"_id": product_id},
            {"$pull": {"ratings": {"user_id": user_id}}}
        )
        self.collection.update_one(
            {"_id": product_id},
            {"$push": {"ratings": {"user_id": user_id, "value": value}}}
        )
        self._recalc_rating(product_id)

    def _recalc_rating(self, product_id: ObjectId):
        product = self.get_by_id(product_id)
        if not product:
            return
        ratings = product.get("ratings", [])
        avg = sum(r["value"] for r in ratings) / len(ratings) if ratings else 0.0
        self.collection.update_one(
            {"_id": product_id},
            {"$set": {"rating": round(avg, 2)}}
        )

    def update(self, product_id: ObjectId, fields: dict):
        return self.collection.update_one(
            {"_id": product_id}, {"$set": fields}
        )

    def delete(self, product_id: ObjectId):
        return self.collection.delete_one({"_id": product_id})

    def count(self):
        return self.collection.count_documents({})