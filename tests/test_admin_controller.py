from controllers.admin_controller import AdminController
from utils.session import Session


def test_is_admin_false(sample_user):
    ctrl = AdminController()
    assert ctrl.is_admin() is False


def test_is_admin_true(sample_user, user_model):
    user_model.collection.update_one(
        {"_id": sample_user["_id"]},
        {"$set": {"is_admin": True}}
    )
    sample_user["is_admin"] = True
    Session.set_user(sample_user)
    
    ctrl = AdminController()
    assert ctrl.is_admin() is True


def test_delete_user_self_fails(sample_user):
    ctrl = AdminController()
    ok, msg = ctrl.delete_user(sample_user["_id"])
    assert not ok
    assert "самого себя" in msg


def test_list_reviews_batch(sample_product, sample_user):
    ctrl = AdminController()
    ctrl.reviews.create(sample_product, sample_user["_id"], "A", 5)
    ctrl.reviews.create(sample_product, sample_user["_id"], "B", 4)
    
    res = ctrl.list_reviews()
    assert len(res) == 2
    assert res[0]["author_login"] == sample_user["login"]
    assert res[0]["product_name"] == "Тестовый товар"