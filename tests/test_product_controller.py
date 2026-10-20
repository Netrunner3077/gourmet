from bson import ObjectId
from controllers.product_controller import ProductController
from utils.session import Session


def test_get_product(sample_product, sample_category):
    ctrl = ProductController()
    p = ctrl.get_product(sample_product)
    assert p["name"] == "Тестовый товар"


def test_get_products_by_ids(sample_product, sample_category):
    ctrl = ProductController()
    p2 = ctrl.products.create("Второй", sample_category, "B", "C")
    
    res = ctrl.get_products_by_ids([sample_product, p2, ObjectId()])
    assert len(res) == 2


def test_rate_product_unauthorized(sample_product):
    Session.logout()
    ctrl = ProductController()
    ok, msg = ctrl.rate_product(sample_product, 5)
    assert not ok
    assert "войдите" in msg


def test_rate_product_authorized(sample_product, sample_user):
    ctrl = ProductController()
    ok, msg = ctrl.rate_product(sample_product, 5)
    assert ok
    
    p = ctrl.get_product(sample_product)
    assert p["rating"] == 5.0
    assert len(p["ratings"]) == 1


def test_toggle_favorite(sample_product, sample_user):
    ctrl = ProductController()
    
    ok, _ = ctrl.toggle_favorite(sample_product)
    assert ok
    assert ctrl.is_favorite(sample_product) is True
    assert len(ctrl.list_favorites()) == 1
    
    ok, _ = ctrl.toggle_favorite(sample_product)
    assert ok
    assert ctrl.is_favorite(sample_product) is False
    assert len(ctrl.list_favorites()) == 0


def test_add_and_remove_from_cart(sample_product, sample_user):
    ctrl = ProductController()
    
    ok, _ = ctrl.add_to_cart(sample_product, 2)
    assert ok
    
    cart_ctrl = ctrl.carts
    cart = cart_ctrl.get_or_create(sample_user["_id"])
    assert cart["items"][0]["quantity"] == 2
    
    ok, _ = ctrl.remove_from_cart(sample_product)
    assert ok
    cart = cart_ctrl.get_or_create(sample_user["_id"])
    assert len(cart["items"]) == 0