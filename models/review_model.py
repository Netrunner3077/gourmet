from bson import ObjectId
from models.database import Database
from utils.time_utils import utcnow


class ReviewModel:
    def __init__(self):
        self.collection = Database().reviews

    def create(self, product_id: ObjectId, user_id: ObjectId, text: str, rating: int):
        doc = {
            "product_id": product_id,
            "user_id": user_id,
            "text": text,
            "rating": int(rating),
            "likes": 0,
            "dislikes": 0,
            "liked_by": [],
            "disliked_by": [],
            "comments": [],
            "created_at": utcnow(),
        }
        return self.collection.insert_one(doc).inserted_id

    def get_by_product(self, product_id: ObjectId):
        return list(
            self.collection.find({"product_id": product_id})
            .sort("created_at", -1)
        )

    def get_by_user(self, user_id: ObjectId):
        return list(
            self.collection.find({"user_id": user_id})
            .sort("created_at", -1)
        )

    def get_by_id(self, review_id: ObjectId):
        return self.collection.find_one({"_id": review_id})

    def list_all(self):
        return list(self.collection.find().sort("created_at", -1))

    def count_by_product(self, product_id: ObjectId) -> int:
        return self.collection.count_documents({"product_id": product_id})

    def count_by_user(self, user_id: ObjectId) -> int:
        return self.collection.count_documents({"user_id": user_id})

    def count_comments_by_user(self, user_id: ObjectId) -> int:
        pipeline = [
            {"$match": {"comments.user_id": user_id}},
            {"$unwind": "$comments"},
            {"$match": {"comments.user_id": user_id}},
            {"$count": "total"},
        ]
        result = list(self.collection.aggregate(pipeline))
        return result[0]["total"] if result else 0

    def toggle_like(self, review_id: ObjectId, user_id: ObjectId):
        review = self.collection.find_one({"_id": review_id})
        if not review:
            return
        liked = user_id in review.get("liked_by", [])
        disliked = user_id in review.get("disliked_by", [])
        update = {}
        if liked:
            update["$pull"] = {"liked_by": user_id}
            update["$inc"] = {"likes": -1}
        else:
            update["$addToSet"] = {"liked_by": user_id}
            update["$inc"] = {"likes": 1}
            if disliked:
                update.setdefault("$pull", {})["disliked_by"] = user_id
                update["$inc"]["dislikes"] = -1
        self.collection.update_one({"_id": review_id}, update)

    def toggle_dislike(self, review_id: ObjectId, user_id: ObjectId):
        review = self.collection.find_one({"_id": review_id})
        if not review:
            return
        disliked = user_id in review.get("disliked_by", [])
        liked = user_id in review.get("liked_by", [])
        update = {}
        if disliked:
            update["$pull"] = {"disliked_by": user_id}
            update["$inc"] = {"dislikes": -1}
        else:
            update["$addToSet"] = {"disliked_by": user_id}
            update["$inc"] = {"dislikes": 1}
            if liked:
                update.setdefault("$pull", {})["liked_by"] = user_id
                update["$inc"]["likes"] = -1
        self.collection.update_one({"_id": review_id}, update)

    def add_comment(self, review_id: ObjectId, user_id: ObjectId, text: str):
        comment = {
            "user_id": user_id,
            "text": text,
            "created_at": utcnow(),
        }
        return self.collection.update_one(
            {"_id": review_id},
            {"$push": {"comments": comment}}
        )

    def delete(self, review_id: ObjectId):
        return self.collection.delete_one({"_id": review_id})