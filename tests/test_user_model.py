from utils.security import verify_password


def test_create_user_returns_id(user_model):
    uid = user_model.create_user("user1", "pass1234")
    assert uid is not None


def test_create_duplicate_login_returns_none(user_model):
    user_model.create_user("dup", "pass1234")
    uid = user_model.create_user("dup", "other123")
    assert uid is None


def test_password_is_hashed(user_model):
    uid = user_model.create_user("user2", "pass1234")
    doc = user_model.get_by_id(uid)
    assert doc["password_hash"] != "pass1234"
    assert verify_password("pass1234", doc["password_hash"])


def test_authenticate_success(user_model):
    user_model.create_user("user3", "pass1234")
    user = user_model.authenticate("user3", "pass1234")
    assert user is not None
    assert user["login"] == "user3"


def test_authenticate_wrong_password(user_model):
    user_model.create_user("user4", "pass1234")
    assert user_model.authenticate("user4", "wrong") is None


def test_authenticate_nonexistent(user_model):
    assert user_model.authenticate("nobody", "pass1234") is None


def test_blocked_user_cannot_authenticate(user_model):
    uid = user_model.create_user("blocked", "pass1234")
    user_model.set_blocked(uid, True)
    assert user_model.authenticate("blocked", "pass1234") is None


def test_get_by_login(user_model):
    user_model.create_user("findme", "pass1234")
    u = user_model.get_by_login("findme")
    assert u is not None and u["login"] == "findme"


def test_update_avatar(user_model):
    uid = user_model.create_user("avatar", "pass1234")
    assert user_model.update_avatar(uid, "resources/avatar.png")
    assert user_model.get_by_id(uid)["avatar"] == "resources/avatar.png"


def test_increment_stat(user_model):
    uid = user_model.create_user("stat", "pass1234")
    user_model.increment_stat(uid, "reviews_count", 1)
    user_model.increment_stat(uid, "reviews_count", 1)
    doc = user_model.get_by_id(uid)
    assert doc["stats"]["reviews_count"] == 2


def test_delete_user(user_model):
    uid = user_model.create_user("todelete", "pass1234")
    user_model.delete(uid)
    assert user_model.get_by_id(uid) is None