"""Controller for business QR actions."""

from models.qr_model import QrModel


class QrController:
    def __init__(self, qr_model: QrModel | None = None):
        self.qr_model = qr_model or QrModel()

    def load_business_qr(self) -> bytes:
        return self.qr_model.download_business_qr()
