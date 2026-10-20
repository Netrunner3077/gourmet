from controllers.auth_controller import AuthController
from utils.session import Session


def test_register_success():
    ctrl = AuthController()
    ok, _ = ctrl.register("newuser", "pass1234", "pass1234")
    assert ok


def test_register_password_mismatch():
    ctrl = AuthController()
    ok, msg = ctrl.register("user1", "pass1234", "other1234")
    assert not ok
    assert "совпадают" in msg.lower()


def test_register_short_login():
    ctrl = AuthController()
    ok, _ = ctrl.register("ab", "pass1234", "pass1234")
    assert not ok


def test_register_short_password():
    ctrl = AuthController()
    ok, _ = ctrl.register("user2", "ab12", "ab12")
    assert not ok


def test_register_duplicate():
    ctrl = AuthController()
    ctrl.register("dup", "pass1234", "pass1234")
    ok, _ = ctrl.register("dup", "other1234", "other1234")
    assert not ok


def test_login_success():
    ctrl = AuthController()
    ctrl.register("loginuser", "pass1234", "pass1234")
    ok, _ = ctrl.login("loginuser", "pass1234")
    assert ok
    assert Session.is_authenticated()


def test_login_wrong_password():
    ctrl = AuthController()
    ctrl.register("u", "pass1234", "pass1234")
    ok, _ = ctrl.login("u", "wrong1234")
    assert not ok
    assert not Session.is_authenticated()


def test_logout():
    ctrl = AuthController()
    ctrl.register("u2", "pass1234", "pass1234")
    ctrl.login("u2", "pass1234")
    ctrl.logout()
    assert not Session.is_authenticated()