from bson import ObjectId
from models.database import Database


class CategoryModel:
    def __init__(self):
        self.collection = Database().categories

    def create(self, name: str, parent_id: ObjectId | None = None) -> ObjectId:
        return self.collection.insert_one(
            {"name": name, "parent_id": parent_id}
        ).inserted_id

    def get_all(self, parent_id=None):
        return list(self.collection.find({"parent_id": parent_id}))

    def get_by_id(self, category_id: ObjectId):
        return self.collection.find_one({"_id": category_id})

    def get_by_name(self, name: str):
        return self.collection.find_one({"name": name})

    def update(self, category_id: ObjectId, name: str):
        return self.collection.update_one(
            {"_id": category_id}, {"$set": {"name": name}}
        )

    def delete(self, category_id: ObjectId):
        return self.collection.delete_one({"_id": category_id})

    def count(self):
        return self.collection.count_documents({})