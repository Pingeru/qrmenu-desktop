"""Authentication and token storage model."""

from __future__ import annotations

from typing import Any

from models.api_client import ApiClient


class AuthModel:
    def __init__(self, api_client: ApiClient | None = None):
        self.api_client = api_client or ApiClient()
        self.api_client.set_unauthorized_handler(self._refresh_access_token_safely)
        self.business: dict[str, Any] | None = None
        self.access_token: str | None = None
        self.refresh_token: str | None = None

    @property
    def is_authenticated(self) -> bool:
        return bool(self.access_token)

    def login_business(self, email: str, password: str) -> dict[str, Any]:
        response = self.api_client.post(
            "/business/auth/login",
            {"email": email, "password": password},
            auth=False,
        )
        self._store_auth_response(response)
        return self.business or {}

    def register_business(
        self,
        name: str,
        email: str,
        password: str,
    ) -> dict[str, Any]:
        payload = {"name": name, "email": email, "password": password}
        response = self.api_client.post("/business/auth/register", payload, auth=False)
        self._store_auth_response(response)
        return self.business or {}

    def forgot_business_password(self, email: str) -> dict[str, Any]:
        return self.api_client.post(
            "/business/auth/forgot-password",
            {"email": email},
            auth=False,
        )

    def refresh_access_token(self) -> str:
        response = self.api_client.post(
            "/business/auth/refresh",
            {"refresh_token": self.refresh_token},
            auth=False,
        )
        self.access_token = response.get("access_token")
        self.api_client.set_access_token(self.access_token)
        return self.access_token or ""

    def update_business(self, **fields: Any) -> dict[str, Any]:
        payload = {key: value for key, value in fields.items() if value is not None}
        response = self.api_client.put("/business/auth/edit", payload)
        self.business = response.get("business", self.business)
        return self.business or {}

    def delete_business(self) -> dict[str, Any]:
        response = self.api_client.delete("/business/auth/delete")
        self.logout()
        return response

    def logout(self):
        self.business = None
        self.access_token = None
        self.refresh_token = None
        self.api_client.set_access_token(None)

    def _store_auth_response(self, response: dict[str, Any]):
        self.business = response.get("business")
        self.access_token = response.get("access_token")
        self.refresh_token = response.get("refresh_token")
        self.api_client.set_access_token(self.access_token)

    def _refresh_access_token_safely(self) -> bool:
        if not self.refresh_token:
            return False
        try:
            self.refresh_access_token()
        except Exception:
            self.logout()
            return False
        return bool(self.access_token)
