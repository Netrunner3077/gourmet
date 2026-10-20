from models.user_model import UserModel
from utils.validators import validate_login, validate_password
from utils.session import Session
from controllers.compare_controller import CompareController


class AuthController:
    def __init__(self):
        self.user_model = UserModel()

    def register(self, login: str, password: str, password2: str) -> tuple[bool, str]:
        if password != password2:
            return False, "Пароли не совпадают."

        ok, msg = validate_login(login)
        if not ok:
            return False, msg

        ok, msg = validate_password(password)
        if not ok:
            return False, msg

        if self.user_model.get_by_login(login):
            return False, "Пользователь с таким логином уже существует."

        user_id = self.user_model.create_user(login, password)
        if not user_id:
            return False, "Не удалось создать пользователя."
        return True, "Регистрация успешна! Теперь войдите."

    def login(self, login: str, password: str) -> tuple[bool, str]:
        user = self.user_model.authenticate(login, password)
        if not user:
            return False, "Неверный логин или пароль, либо аккаунт заблокирован."
        CompareController.clear()
        Session.set_user(user)
        return True, "Вход выполнен."

    def logout(self):
        CompareController.clear()
        Session.logout()