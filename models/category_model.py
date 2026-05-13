"""Category API integration model."""

from __future__ import annotations

from typing import Any

from models.api_client import ApiClient


class CategoryModel:
    def __init__(self, api_client: ApiClient | None = None):
        self.api_client = api_client or ApiClient()

    def list_categories(self) -> list[dict[str, Any]]:
        response = self.api_client.get("/business/categories")
        return response.get("categories", [])

    def get_category(self, category_id: str) -> dict[str, Any]:
        response = self.api_client.get(f"/business/categories/{category_id}")
        return response.get("category", {})

    def create_category(self, name: str) -> dict[str, Any]:
        response = self.api_client.post("/business/categories", {"name": name})
        return response.get("category", {})

    def update_category(self, category_id: str, name: str) -> dict[str, Any]:
        response = self.api_client.put(f"/business/categories/{category_id}", {"name": name})
        return response.get("category", {})

    def delete_category(self, category_id: str) -> dict[str, Any]:
        return self.api_client.delete(f"/business/categories/{category_id}")
