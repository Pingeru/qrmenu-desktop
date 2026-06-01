"""Controller for business order actions."""

from models.order_model import OrderModel


class OrderController:
    def __init__(self, order_model: OrderModel | None = None):
        self.order_model = order_model or OrderModel()

    def load_orders(self, from_date: str | None = None, to_date: str | None = None):
        return self.order_model.list_business_orders(from_date=from_date, to_date=to_date)

    def update_order_status(self, order_id: str, status: str):
        return self.order_model.update_order_status(order_id, status)

    def delete_order(self, order_id: str):
        return self.order_model.delete_order(order_id)
