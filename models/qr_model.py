"""Business QR API integration model."""

from __future__ import annotations

from models.api_client import ApiClient


class QrModel:
    def __init__(self, api_client: ApiClient | None = None):
        self.api_client = api_client or ApiClient()

    def download_business_qr(self) -> bytes:
        return self.api_client.get_bytes("/business/qr/")
