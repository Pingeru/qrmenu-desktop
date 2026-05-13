"""HTTP client for backend requests."""

from __future__ import annotations

from typing import Any

import requests

from utils.config import API_BASE_URL, API_TIMEOUT_SECONDS


class ApiError(Exception):
    """Raised when the backend cannot complete a request."""

    def __init__(self, message: str, status_code: int | None = None, payload: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


class ApiClient:
    def __init__(self, base_url: str = API_BASE_URL, timeout: float = API_TIMEOUT_SECONDS):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.access_token: str | None = None
        self.unauthorized_handler = None

    def set_access_token(self, access_token: str | None):
        self.access_token = access_token

    def set_unauthorized_handler(self, handler):
        self.unauthorized_handler = handler

    def get(self, path: str, *, auth: bool = True) -> dict[str, Any]:
        return self.request("GET", path, auth=auth)

    def post(self, path: str, payload: dict[str, Any] | None = None, *, auth: bool = True) -> dict[str, Any]:
        return self.request("POST", path, json_payload=payload, auth=auth)

    def put(self, path: str, payload: dict[str, Any] | None = None, *, auth: bool = True) -> dict[str, Any]:
        return self.request("PUT", path, json_payload=payload, auth=auth)

    def delete(self, path: str, *, auth: bool = True) -> dict[str, Any]:
        return self.request("DELETE", path, auth=auth)

    def request(
        self,
        method: str,
        path: str,
        *,
        json_payload: dict[str, Any] | None = None,
        auth: bool = True,
    ) -> dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        headers = {"Accept": "application/json"}
        if json_payload is not None:
            headers["Content-Type"] = "application/json"
        if auth and self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"

        try:
            response = requests.request(
                method,
                url,
                json=json_payload,
                headers=headers,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise ApiError(f"Backend request failed: {exc}") from exc

        if response.status_code == 401 and auth and self.unauthorized_handler:
            try:
                refreshed = self.unauthorized_handler()
            except ApiError:
                refreshed = False
            if refreshed:
                headers["Authorization"] = f"Bearer {self.access_token}"
                try:
                    response = requests.request(
                        method,
                        url,
                        json=json_payload,
                        headers=headers,
                        timeout=self.timeout,
                    )
                except requests.RequestException as exc:
                    raise ApiError(f"Backend request failed: {exc}") from exc

        payload: Any = {}
        if response.content:
            try:
                payload = response.json()
            except ValueError:
                payload = {"raw": response.text}

        if response.status_code >= 400:
            message = payload.get("error") if isinstance(payload, dict) else None
            raise ApiError(message or f"Backend returned HTTP {response.status_code}", response.status_code, payload)

        return payload if isinstance(payload, dict) else {"data": payload}
