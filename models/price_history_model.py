from utils.time_utils import utcnow
from bson import ObjectId
from models.database import Database


class PriceHistoryModel:
    def __init__(self):
        self.collection = Database().price_history

    def add(self, product_id: ObjectId, price: float, store: str = ""):
        return self.collection.insert_one({
            "product_id": product_id,
            "date": utcnow(),
            "price": float(price),
            "store": store,
        }).inserted_id

    def get_by_product(self, product_id: ObjectId):
        return list(
            self.collection.find({"product_id": product_id}).sort("date", 1)
        )