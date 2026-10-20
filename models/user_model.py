from bson import ObjectId
from models.database import Database
from utils.security import hash_password, verify_password
from utils.time_utils import utcnow


class UserModel:
    def __init__(self):
        self.collection = Database().users

    def create_user(self, login: str, password: str,
                    avatar: str = None) -> ObjectId | None:
        if self.collection.find_one({"login": login}):
            return None

        doc = {
            "login": login,
            "password_hash": hash_password(password),
            "avatar": avatar,
            "created_at": utcnow(),
            "stats": {"reviews_count": 0, "comments_count": 0},
            "is_admin": False,
            "is_blocked": False,
        }
        result = self.collection.insert_one(doc)
        return result.inserted_id

    def authenticate(self, login: str, password: str) -> dict | None:
        user = self.collection.find_one({"login": login})
        if not user:
            return None
        if user.get("is_blocked"):
            return None
        if verify_password(password, user["password_hash"]):
            return user
        return None

    def get_by_id(self, user_id: ObjectId) -> dict | None:
        return self.collection.find_one({"_id": user_id})

    def get_by_login(self, login: str) -> dict | None:
        return self.collection.find_one({"login": login})

    def get_many_by_ids(self, ids: list[ObjectId]) -> list[dict]:
        if not ids:
            return []
        return list(self.collection.find({"_id": {"$in": ids}}))

    def update_avatar(self, user_id: ObjectId, avatar_path: str) -> bool:
        res = self.collection.update_one(
            {"_id": user_id},
            {"$set": {"avatar": avatar_path}}
        )
        return res.modified_count > 0

    def update_password(self, user_id: ObjectId, new_hash: str):
        self.collection.update_one(
            {"_id": user_id},
            {"$set": {"password_hash": new_hash}}
        )

    def increment_stat(self, user_id: ObjectId, field: str, delta: int = 1):
        self.collection.update_one(
            {"_id": user_id},
            {"$inc": {f"stats.{field}": delta}}
        )

    def list_all(self):
        return list(self.collection.find())

    def set_blocked(self, user_id: ObjectId, blocked: bool):
        self.collection.update_one(
            {"_id": user_id},
            {"$set": {"is_blocked": blocked}}
        )

    def delete(self, user_id: ObjectId):
        self.collection.delete_one({"_id": user_id})