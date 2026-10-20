def test_create_and_get(category_model):
    cid = category_model.create("Напитки")
    cat = category_model.get_by_id(cid)
    assert cat["name"] == "Напитки"


def test_get_by_name(category_model):
    category_model.create("Молочное")
    cat = category_model.get_by_name("Молочное")
    assert cat is not None


def test_get_all(category_model):
    category_model.create("A")
    category_model.create("B")
    category_model.create("C")
    assert len(category_model.get_all()) == 3


def test_update(category_model):
    cid = category_model.create("Old")
    category_model.update(cid, "New")
    assert category_model.get_by_id(cid)["name"] == "New"


def test_delete(category_model):
    cid = category_model.create("ToDelete")
    category_model.delete(cid)
    assert category_model.get_by_id(cid) is None


def test_count(category_model):
    assert category_model.count() == 0
    category_model.create("X")
    category_model.create("Y")
    assert category_model.count() == 2