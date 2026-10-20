from bson import ObjectId
from models.price_history_model import PriceHistoryModel


def test_add_price_point(sample_product):
    model = PriceHistoryModel()
    model.add(sample_product, 100.0, "Пятерочка")
    
    history = model.get_by_product(sample_product)
    assert len(history) == 1
    assert history[0]["price"] == 100.0
    assert history[0]["store"] == "Пятерочка"


def test_get_by_product_sorted(sample_product):
    model = PriceHistoryModel()
    model.add(sample_product, 100.0)
    model.add(sample_product, 120.0)
    
    history = model.get_by_product(sample_product)
    assert len(history) == 2
    assert history[0]["price"] == 100.0