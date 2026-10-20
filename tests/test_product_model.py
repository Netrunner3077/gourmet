from bson import ObjectId


def test_create_product(product_model, sample_category):
    pid = product_model.create(
        name="Молоко",
        category_id=sample_category,
        brand="Brand",
        composition="Молоко",
        current_price=99.9,
    )
    assert pid is not None


def test_get_by_id(product_model, sample_product):
    p = product_model.get_by_id(sample_product)
    assert p["name"] == "Тестовый товар"


def test_get_all_by_category(product_model, sample_category):
    product_model.create("A", sample_category, "B", "c", current_price=1)
    product_model.create("B", sample_category, "B", "c", current_price=1)

    other_cat = ObjectId()
    product_model.create("C", other_cat, "B", "c", current_price=1)

    result = product_model.get_all(category_id=sample_category)
    assert len(result) == 2


def test_search_by_name(product_model, sample_category):
    product_model.create("Молоко цельное", sample_category, "B", "c", current_price=1)
    product_model.create("Сыр", sample_category, "B", "c", current_price=1)

    result = product_model.get_all(search="молок")
    assert len(result) == 1


def test_search_case_insensitive(product_model, sample_category):
    product_model.create("Кола", sample_category, "B", "c", current_price=1)
    result = product_model.get_all(search="КОЛА")
    assert len(result) == 1


def test_rating_average(product_model, sample_product):
    u1 = ObjectId()
    u2 = ObjectId()
    product_model.add_or_update_rating(sample_product, u1, 5)
    product_model.add_or_update_rating(sample_product, u2, 3)

    p = product_model.get_by_id(sample_product)
    assert abs(p["rating"] - 4.0) < 0.01


def test_rating_upsert(product_model, sample_product):
    u1 = ObjectId()
    product_model.add_or_update_rating(sample_product, u1, 5)
    product_model.add_or_update_rating(sample_product, u1, 2)

    p = product_model.get_by_id(sample_product)
    assert p["rating"] == 2.0
    assert len(p["ratings"]) == 1


def test_rating_clamped(product_model, sample_product):
    u1 = ObjectId()
    product_model.add_or_update_rating(sample_product, u1, 99)
    p = product_model.get_by_id(sample_product)
    assert p["ratings"][0]["value"] == 5

    product_model.add_or_update_rating(sample_product, u1, -5)
    p = product_model.get_by_id(sample_product)
    assert p["ratings"][0]["value"] == 1


def test_get_many_by_ids(product_model, sample_category):
    a = product_model.create("A", sample_category, "b", "c", current_price=1)
    b = product_model.create("B", sample_category, "b", "c", current_price=1)
    result = product_model.get_many_by_ids([a, b, ObjectId()])
    assert len(result) == 2


def test_update_product(product_model, sample_product):
    product_model.update(sample_product, {"current_price": 555.0})
    p = product_model.get_by_id(sample_product)
    assert p["current_price"] == 555.0


def test_delete_product(product_model, sample_product):
    product_model.delete(sample_product)
    assert product_model.get_by_id(sample_product) is None