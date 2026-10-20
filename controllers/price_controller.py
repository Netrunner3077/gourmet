from datetime import timedelta
from bson import ObjectId
from models.price_history_model import PriceHistoryModel
from models.product_model import ProductModel
from utils.time_utils import utcnow


class PriceController:
    def __init__(self):
        self.history = PriceHistoryModel()
        self.products = ProductModel()

    def get_history(self, product_id: ObjectId) -> list[dict]:
        return self.history.get_by_product(product_id)

    def get_stats(self, product_id: ObjectId) -> dict:
        history = self.get_history(product_id)
        if not history:
            return {
                "min": 0, "max": 0, "avg": 0,
                "current": 0, "delta_pct": 0, "count": 0,
            }
        prices = [h["price"] for h in history]
        min_p = min(prices)
        max_p = max(prices)
        avg = sum(prices) / len(prices)
        first = prices[0]
        last = prices[-1]
        delta = ((last - first) / first * 100) if first else 0
        return {
            "min": min_p,
            "max": max_p,
            "avg": round(avg, 2),
            "current": last,
            "delta_pct": round(delta, 1),
            "count": len(history),
        }

    def add_price_point(self, product_id: ObjectId,
                        price: float, store: str) -> tuple[bool, str]:
        if price <= 0:
            return False, "Цена должна быть больше нуля."
        self.history.add(product_id, price, store or "—")

        product = self.products.get_by_id(product_id)
        if product:
            self.products.update(product_id, {"current_price": float(price)})
        return True, "Точка цены добавлена."

    def grouped_by_store(self, product_id: ObjectId) -> dict:
        history = self.get_history(product_id)
        result = {}
        for h in history:
            store = h.get("store", "—")
            result.setdefault(store, []).append(h["price"])
        return result

    def last_days(self, product_id: ObjectId, days: int = 30) -> list[dict]:
        cutoff = utcnow() - timedelta(days=days)
        return [h for h in self.get_history(product_id) if h["date"] >= cutoff]