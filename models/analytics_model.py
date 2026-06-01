"""Business analytics API integration model."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

from models.api_client import ApiClient


class AnalyticsModel:
    def __init__(self, api_client: ApiClient | None = None):
        self.api_client = api_client or ApiClient()

    def get_business_analytics(self, from_date: str | None = None, to_date: str | None = None) -> dict[str, Any]:
        params = {}
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        path = "/business/analytics"
        if params:
            path = f"{path}?{urlencode(params)}"
        return self.api_client.get(path)
