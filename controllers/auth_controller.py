"""Controller for authentication flow."""

from models.auth_model import AuthModel


class AuthController:
    def __init__(self, auth_model: AuthModel | None = None):
        self.auth_model = auth_model or AuthModel()

    def login_business(self, email: str, password: str):
        return self.auth_model.login_business(email, password)

    def register_business(self, name: str, email: str, password: str, qr_base_url: str | None = None):
        return self.auth_model.register_business(name, email, password, qr_base_url)

    def update_business(self, **fields):
        return self.auth_model.update_business(**fields)

    def delete_business(self):
        return self.auth_model.delete_business()

    def logout(self):
        self.auth_model.logout()
