import re

LOGIN_RE = re.compile(r"^[A-Za-z0-9_]{4,20}$")


def validate_login(login: str) -> tuple[bool, str]:
    if not login or len(login) < 4:
        return False, "Логин должен быть не менее 4 символов."
    if not LOGIN_RE.match(login):
        return False, "Логин: только буквы, цифры и _, 4–20 символов."
    return True, ""


def validate_password(password: str) -> tuple[bool, str]:
    if not password or len(password) < 6:
        return False, "Пароль должен быть не менее 6 символов."
    if password.isdigit() or password.isalpha():
        return False, "Пароль должен содержать буквы и цифры."
    return True, ""