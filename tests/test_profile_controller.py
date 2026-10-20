from controllers.profile_controller import ProfileController
from utils.security import verify_password


def test_change_password_wrong_old(sample_user):
    ctrl = ProfileController()
    ok, msg = ctrl.change_password("wrongpass", "newpass123", "newpass123")
    assert not ok
    assert "неверно" in msg


def test_change_password_mismatch(sample_user):
    ctrl = ProfileController()
    ok, msg = ctrl.change_password("pass1234", "newpass123", "different")
    assert not ok
    assert "не совпадают" in msg


def test_change_password_weak_new(sample_user):
    ctrl = ProfileController()
    ok, msg = ctrl.change_password("pass1234", "123", "123")
    assert not ok
    assert "6 символов" in msg


def test_change_password_same_as_old(sample_user):
    ctrl = ProfileController()
    ok, msg = ctrl.change_password("pass1234", "pass1234", "pass1234")
    assert not ok
    assert "совпадает со старым" in msg


def test_change_password_success(sample_user, user_model):
    ctrl = ProfileController()
    ok, msg = ctrl.change_password("pass1234", "newpass123", "newpass123")
    assert ok
    
    user = user_model.get_by_id(sample_user["_id"])
    assert verify_password("newpass123", user["password_hash"])


def test_get_stats(sample_user, sample_product):
    ctrl = ProfileController()
    
    ctrl.reviews.create(sample_product, sample_user["_id"], "A", 5)
    ctrl.favorites.add(sample_user["_id"], sample_product)
    
    stats = ctrl.get_stats()
    assert stats["reviews"] == 1
    assert stats["favorites"] == 1
    assert stats["comments"] == 0