class Session:
    _current_user = None

    @classmethod
    def set_user(cls, user_doc: dict):
        cls._current_user = user_doc

    @classmethod
    def get_user(cls) -> dict | None:
        return cls._current_user

    @classmethod
    def get_user_id(cls):
        return cls._current_user["_id"] if cls._current_user else None

    @classmethod
    def is_authenticated(cls) -> bool:
        return cls._current_user is not None

    @classmethod
    def refresh(cls) -> bool:
        """Обновляет данные из БД. Возвращает False, если юзер удалён или заблокирован."""
        if not cls._current_user:
            return False
        from models.user_model import UserModel
        user = UserModel().get_by_id(cls._current_user["_id"])
        if not user or user.get("is_blocked"):
            cls.logout()
            return False
        cls._current_user = user
        return True

    @classmethod
    def logout(cls):
        cls._current_user = None