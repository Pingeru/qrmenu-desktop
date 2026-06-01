"""Product API integration model."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from models.api_client import ApiClient, ApiError


class ProductModel:
    def __init__(self, api_client: ApiClient | None = None):
        self.api_client = api_client or ApiClient()

    def list_products_by_category(self, category_id: str) -> list[dict[str, Any]]:
        response = self.api_client.get(f"/business/products/category/{category_id}", auth=False)
        return response.get("products", [])

    def list_products(
        self,
        *,
        business_id: str | None = None,
        category_id: str | None = None,
        is_active: bool | None = None,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if business_id:
            params["business_id"] = business_id
        if category_id:
            params["category_id"] = category_id
        if is_active is not None:
            params["is_active"] = str(is_active).lower()

        path = "/business/products"
        if params:
            path = f"{path}?{urlencode(params)}"
        response = self.api_client.get(path, auth=False)
        return response.get("products", [])

    def get_product(self, product_id: str) -> dict[str, Any]:
        response = self.api_client.get(f"/business/products/{product_id}", auth=False)
        return response.get("product", {})

    def create_product(
        self,
        *,
        name: str,
        category_id: str,
        price: float,
        description: str = "",
        is_active: bool = True,
        image_path: str | None = None,
    ) -> dict[str, Any]:
        payload = {
            "name": name,
            "description": description,
            "category_id": category_id,
            "price": price,
            "is_active": is_active,
        }
        response = self._send_product_form("POST", "/business/products", payload, image_path)
        return response.get("product", {})

    def update_product(
        self,
        product_id: str,
        *,
        name: str,
        category_id: str,
        price: float,
        description: str = "",
        is_active: bool = True,
        image_path: str | None = None,
    ) -> dict[str, Any]:
        payload = {
            "name": name,
            "description": description,
            "category_id": category_id,
            "price": price,
            "is_active": is_active,
        }
        response = self._send_product_form(
            "PUT",
            f"/business/products/{product_id}",
            payload,
            image_path,
        )
        return response.get("product", {})

    def delete_product(self, product_id: str) -> dict[str, Any]:
        return self.api_client.delete(f"/business/products/{product_id}")

    def _send_product_form(
        self,
        method: str,
        path: str,
        payload: dict[str, Any],
        image_path: str | None,
    ) -> dict[str, Any]:
        if not image_path or image_path.startswith("http"):
            if method == "POST":
                return self.api_client.post(path, payload)
            return self.api_client.put(path, payload)

        path_obj = Path(image_path)
        if not path_obj.is_file():
            raise ApiError(f"Image file not found: {image_path}")
        with path_obj.open("rb") as image_file:
            files = {"image": (path_obj.name, image_file)}
            if method == "POST":
                return self.api_client.post_form(path, payload, files=files)
            return self.api_client.put_form(path, payload, files=files)
