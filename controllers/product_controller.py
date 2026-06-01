"""Controller for product actions."""

from models.product_model import ProductModel


class ProductController:
    def __init__(self, product_model: ProductModel | None = None):
        self.product_model = product_model or ProductModel()

    def load_products_by_category(self, category_id: str):
        return self.product_model.list_products_by_category(category_id)

    def load_products(self, business_id: str | None = None, category_id: str | None = None, is_active: bool | None = None):
        return self.product_model.list_products(
            business_id=business_id,
            category_id=category_id,
            is_active=is_active,
        )

    def get_product(self, product_id: str):
        return self.product_model.get_product(product_id)

    def create_product(self, **fields):
        return self.product_model.create_product(**fields)

    def update_product(self, product_id: str, **fields):
        return self.product_model.update_product(product_id, **fields)

    def delete_product(self, product_id: str):
        return self.product_model.delete_product(product_id)
