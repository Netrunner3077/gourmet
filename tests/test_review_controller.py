from bson import ObjectId
from controllers.review_controller import ReviewController
from utils.session import Session


def test_add_review_unauthorized(sample_product):
    Session.logout()
    ctrl = ReviewController()
    ok, msg = ctrl.add_review(sample_product, "Хорошо", 5)
    assert not ok
    assert "войдите" in msg


def test_add_review_empty_text(sample_product, sample_user):
    ctrl = ReviewController()
    ok, msg = ctrl.add_review(sample_product, "   ", 5)
    assert not ok
    assert "пустым" in msg


def test_add_review_invalid_rating(sample_product, sample_user):
    ctrl = ReviewController()
    ok, msg = ctrl.add_review(sample_product, "Норм", 6)
    assert not ok
    assert "от 1 до 5" in msg


def test_add_review_success(sample_product, sample_user):
    ctrl = ReviewController()
    ok, _ = ctrl.add_review(sample_product, "Отличный товар", 5)
    assert ok
    
    reviews = ctrl.list_reviews(sample_product)
    assert len(reviews) == 1
    assert reviews[0]["text"] == "Отличный товар"
    assert reviews[0]["author_login"] == sample_user["login"]


def test_delete_review_by_author(sample_product, sample_user):
    ctrl = ReviewController()
    ctrl.add_review(sample_product, "Текст", 5)
    reviews = ctrl.list_reviews(sample_product)
    rid = reviews[0]["_id"]
    
    ok, _ = ctrl.delete_review(rid)
    assert ok
    assert len(ctrl.list_reviews(sample_product)) == 0


def test_delete_review_by_stranger_fails(sample_product, sample_user, user_model):
    ctrl = ReviewController()
    ctrl.add_review(sample_product, "Текст", 5)
    reviews = ctrl.list_reviews(sample_product)
    rid = reviews[0]["_id"]
    
    stranger_id = user_model.create_user("stranger", "pass1234")
    stranger = user_model.get_by_id(stranger_id)
    Session.set_user(stranger)
    
    ok, msg = ctrl.delete_review(rid)
    assert not ok
    assert "Нет прав" in msg


def test_toggle_like(sample_product, sample_user):
    ctrl = ReviewController()
    ctrl.add_review(sample_product, "Текст", 5)
    rid = ctrl.list_reviews(sample_product)[0]["_id"]
    
    ctrl.toggle_like(rid)
    r = ctrl.list_reviews(sample_product)[0]
    assert r["likes"] == 1
    
    ctrl.toggle_like(rid)
    r = ctrl.list_reviews(sample_product)[0]
    assert r["likes"] == 0