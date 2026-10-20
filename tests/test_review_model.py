from bson import ObjectId


def test_create_review(review_model, sample_product, sample_user):
    rid = review_model.create(
        sample_product, sample_user["_id"], "Хороший товар", 5
    )
    assert rid is not None


def test_get_by_product(review_model, sample_product, sample_user):
    review_model.create(sample_product, sample_user["_id"], "A", 5)
    review_model.create(sample_product, sample_user["_id"], "B", 4)
    result = review_model.get_by_product(sample_product)
    assert len(result) == 2


def test_get_by_user(review_model, sample_product, sample_user):
    review_model.create(sample_product, sample_user["_id"], "A", 5)
    result = review_model.get_by_user(sample_user["_id"])
    assert len(result) == 1


def test_toggle_like(review_model, sample_product, sample_user):
    rid = review_model.create(sample_product, sample_user["_id"], "A", 5)
    other = ObjectId()

    review_model.toggle_like(rid, other)
    r = review_model.collection.find_one({"_id": rid})
    assert r["likes"] == 1
    assert other in r["liked_by"]

    review_model.toggle_like(rid, other)
    r = review_model.collection.find_one({"_id": rid})
    assert r["likes"] == 0


def test_toggle_dislike(review_model, sample_product, sample_user):
    rid = review_model.create(sample_product, sample_user["_id"], "A", 5)
    other = ObjectId()

    review_model.toggle_dislike(rid, other)
    r = review_model.collection.find_one({"_id": rid})
    assert r["dislikes"] == 1

    review_model.toggle_dislike(rid, other)
    r = review_model.collection.find_one({"_id": rid})
    assert r["dislikes"] == 0


def test_like_removes_dislike(review_model, sample_product, sample_user):
    rid = review_model.create(sample_product, sample_user["_id"], "A", 5)
    other = ObjectId()

    review_model.toggle_dislike(rid, other)
    review_model.toggle_like(rid, other)

    r = review_model.collection.find_one({"_id": rid})
    assert r["likes"] == 1
    assert r["dislikes"] == 0
    assert other not in r["disliked_by"]


def test_add_comment(review_model, sample_product, sample_user):
    rid = review_model.create(sample_product, sample_user["_id"], "A", 5)
    other = ObjectId()

    review_model.add_comment(rid, other, "Комментарий")
    r = review_model.collection.find_one({"_id": rid})
    assert len(r["comments"]) == 1
    assert r["comments"][0]["text"] == "Комментарий"


def test_delete_review(review_model, sample_product, sample_user):
    rid = review_model.create(sample_product, sample_user["_id"], "A", 5)
    review_model.delete(rid)
    assert review_model.collection.find_one({"_id": rid}) is None


def test_count_by_product(review_model, sample_product, sample_user):
    review_model.create(sample_product, sample_user["_id"], "A", 5)
    review_model.create(sample_product, sample_user["_id"], "B", 4)
    assert review_model.count_by_product(sample_product) == 2