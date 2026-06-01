"""Business order API integration model."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

from models.api_client import ApiClient


class OrderModel:
    def __init__(self, api_client: ApiClient | None = None):
        self.api_client = api_client or ApiClient()

    def list_business_orders(self, from_date: str | None = None, to_date: str | None = None) -> list[dict[str, Any]]:
        params = {}
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        path = "/business/orders"
        if params:
            path = f"{path}?{urlencode(params)}"
        response = self.api_client.get(path)
        return response.get("orders", [])

    def update_order_status(self, order_id: str, status: str) -> dict[str, Any]:
        response = self.api_client.put(
            f"/business/orders/{order_id}",
            {"status": status},
        )
        return response.get("order", {})

    def delete_order(self, order_id: str) -> dict[str, Any]:
        return self.api_client.delete(f"/business/orders/{order_id}")
