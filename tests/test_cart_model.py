from bson import ObjectId


def test_get_or_create_new(cart_model):
    uid = ObjectId()
    cart = cart_model.get_or_create(uid)
    assert cart["items"] == []


def test_get_or_create_existing(cart_model):
    uid = ObjectId()
    c1 = cart_model.get_or_create(uid)
    c2 = cart_model.get_or_create(uid)
    assert c1["_id"] == c2["_id"]


def test_add_item_new(cart_model, sample_product):
    uid = ObjectId()
    cart_model.add_item(uid, sample_product, 2)
    cart = cart_model.get_or_create(uid)
    assert len(cart["items"]) == 1
    assert cart["items"][0]["quantity"] == 2


def test_add_item_increment(cart_model, sample_product):
    uid = ObjectId()
    cart_model.add_item(uid, sample_product, 1)
    cart_model.add_item(uid, sample_product, 3)
    cart = cart_model.get_or_create(uid)
    assert len(cart["items"]) == 1
    assert cart["items"][0]["quantity"] == 4


def test_set_quantity(cart_model, sample_product):
    uid = ObjectId()
    cart_model.add_item(uid, sample_product, 1)
    cart_model.set_quantity(uid, sample_product, 7)
    cart = cart_model.get_or_create(uid)
    assert cart["items"][0]["quantity"] == 7


def test_remove_item(cart_model, sample_product):
    uid = ObjectId()
    cart_model.add_item(uid, sample_product, 1)
    cart_model.remove_item(uid, sample_product)
    cart = cart_model.get_or_create(uid)
    assert cart["items"] == []


def test_clear(cart_model, sample_product):
    uid = ObjectId()
    other = ObjectId()
    cart_model.add_item(uid, sample_product, 1)
    cart_model.add_item(uid, other, 1)
    cart_model.clear(uid)
    cart = cart_model.get_or_create(uid)
    assert cart["items"] == []


def test_count_total_items(cart_model, sample_product):
    uid = ObjectId()
    cart_model.add_item(uid, sample_product, 2)
    cart_model.add_item(uid, ObjectId(), 3)
    assert cart_model.count_total_items(uid) == 5