from utils.validators import validate_login, validate_password


def test_login_valid():
    ok, _ = validate_login("user_01")
    assert ok


def test_login_too_short():
    ok, msg = validate_login("ab")
    assert not ok
    assert "4" in msg


def test_login_bad_chars():
    ok, _ = validate_login("user name!")
    assert not ok


def test_login_empty():
    ok, _ = validate_login("")
    assert not ok


def test_password_valid():
    ok, _ = validate_password("abc12345")
    assert ok


def test_password_too_short():
    ok, _ = validate_password("ab12")
    assert not ok


def test_password_only_digits():
    ok, _ = validate_password("12345678")
    assert not ok


def test_password_only_letters():
    ok, _ = validate_password("abcdefgh")
    assert not ok


def test_password_empty():
    ok, _ = validate_password("")
    assert not ok