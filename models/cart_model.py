from bson import ObjectId
from models.database import Database
from utils.time_utils import utcnow


class CartModel:
    def __init__(self):
        self.collection = Database().carts

    def get_or_create(self, user_id: ObjectId) -> dict:
        cart = self.collection.find_one({"user_id": user_id})
        if not cart:
            cart = {
                "user_id": user_id,
                "items": [],
                "updated_at": utcnow(),
            }
            cart["_id"] = self.collection.insert_one(cart).inserted_id
        return cart

    def add_item(self, user_id: ObjectId, product_id: ObjectId, quantity: int = 1):
        self.get_or_create(user_id)
        cart = self.collection.find_one(
            {"user_id": user_id, "items.product_id": product_id}
        )
        if cart:
            self.collection.update_one(
                {"user_id": user_id, "items.product_id": product_id},
                {
                    "$inc": {"items.$.quantity": quantity},
                    "$set": {"updated_at": utcnow()},
                }
            )
        else:
            self.collection.update_one(
                {"user_id": user_id},
                {
                    "$push": {"items": {
                        "product_id": product_id,
                        "quantity": quantity,
                    }},
                    "$set": {"updated_at": utcnow()},
                }
            )

    def remove_item(self, user_id: ObjectId, product_id: ObjectId):
        self.collection.update_one(
            {"user_id": user_id},
            {
                "$pull": {"items": {"product_id": product_id}},
                "$set": {"updated_at": utcnow()},
            }
        )

    def clear(self, user_id: ObjectId):
        self.collection.update_one(
            {"user_id": user_id},
            {"$set": {"items": [], "updated_at": utcnow()}}
        )

    def set_quantity(self, user_id, product_id, quantity: int):
        """Устанавливает конкретное количество для товара в корзине."""
        res = self.collection.update_one(
            {"user_id": user_id, "items.product_id": product_id},
            {"$set": {
                "items.$.quantity": quantity,
                "updated_at": utcnow(),
            }}
        )
        if res.matched_count == 0:
            self.collection.update_one(
                {"user_id": user_id},
                {
                    "$push": {"items": {
                        "product_id": product_id,
                        "quantity": quantity,
                    }},
                    "$set": {"updated_at": utcnow()},
                }
            )

    def count_total_items(self, user_id) -> int:
        cart = self.collection.find_one({"user_id": user_id})
        if not cart:
            return 0
        return sum(int(i.get("quantity", 1))
                    for i in cart.get("items", []))