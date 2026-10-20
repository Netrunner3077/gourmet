from bson import ObjectId


class CompareController:
    """Хранит выбранные для сравнения товары в рамках сессии."""
    _selected: list = []
    MAX = 4

    @classmethod
    def toggle(cls, product_id: ObjectId) -> tuple[bool, str]:
        if product_id in cls._selected:
            cls._selected.remove(product_id)
            return True, "Удалено из сравнения."
        if len(cls._selected) >= cls.MAX:
            return False, f"Можно сравнивать не более {cls.MAX} товаров."
        cls._selected.append(product_id)
        return True, "Добавлено к сравнению."

    @classmethod
    def remove(cls, product_id: ObjectId):
        if product_id in cls._selected:
            cls._selected.remove(product_id)

    @classmethod
    def clear(cls):
        cls._selected.clear()

    @classmethod
    def is_selected(cls, product_id: ObjectId) -> bool:
        return product_id in cls._selected

    @classmethod
    def get_selected(cls) -> list:
        return list(cls._selected)

    @classmethod
    def count(cls) -> int:
        return len(cls._selected)