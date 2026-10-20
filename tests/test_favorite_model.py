from bson import ObjectId


def test_add_creates_record(favorite_model):
    uid = ObjectId()
    pid = ObjectId()
    favorite_model.add(uid, pid)
    assert favorite_model.is_favorite(uid, pid)


def test_add_is_idempotent(favorite_model):
    uid = ObjectId()
    pid = ObjectId()
    favorite_model.add(uid, pid)
    favorite_model.add(uid, pid)
    count = favorite_model.collection.count_documents(
        {"user_id": uid, "product_id": pid}
    )
    assert count == 1


def test_remove(favorite_model):
    uid = ObjectId()
    pid = ObjectId()
    favorite_model.add(uid, pid)
    favorite_model.remove(uid, pid)
    assert not favorite_model.is_favorite(uid, pid)


def test_remove_nonexistent_does_not_fail(favorite_model):
    favorite_model.remove(ObjectId(), ObjectId())


def test_toggle_adds_then_removes(favorite_model):
    uid = ObjectId()
    pid = ObjectId()

    result = favorite_model.toggle(uid, pid)
    assert result is True
    assert favorite_model.is_favorite(uid, pid)

    result = favorite_model.toggle(uid, pid)
    assert result is False
    assert not favorite_model.is_favorite(uid, pid)


def test_is_favorite_for_other_user(favorite_model):
    uid1 = ObjectId()
    uid2 = ObjectId()
    pid = ObjectId()
    favorite_model.add(uid1, pid)
    assert not favorite_model.is_favorite(uid2, pid)


def test_get_user_products(favorite_model):
    uid = ObjectId()
    pid1 = ObjectId()
    pid2 = ObjectId()
    pid3 = ObjectId()
    favorite_model.add(uid, pid1)
    favorite_model.add(uid, pid2)
    favorite_model.add(ObjectId(), pid3)

    result = favorite_model.get_user_products(uid)
    assert len(result) == 2
    assert pid1 in result
    assert pid2 in result
    assert pid3 not in result


def test_get_user_products_empty(favorite_model):
    assert favorite_model.get_user_products(ObjectId()) == []