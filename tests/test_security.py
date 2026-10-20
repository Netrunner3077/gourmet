from utils.security import hash_password, verify_password


def test_hash_is_not_plain():
    h = hash_password("secret123")
    assert h != "secret123"
    assert len(h) > 20


def test_hash_is_salted():
    h1 = hash_password("same")
    h2 = hash_password("same")
    assert h1 != h2


def test_verify_correct_password():
    h = hash_password("hello123")
    assert verify_password("hello123", h)


def test_verify_wrong_password():
    h = hash_password("hello123")
    assert not verify_password("hello124", h)


def test_verify_invalid_hash_returns_false():
    assert not verify_password("abc", "")
    assert not verify_password("abc", "not-a-hash")