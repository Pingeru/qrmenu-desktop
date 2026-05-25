"""Controller for product actions."""

from models.product_model import ProductModel


class ProductController:
    def __init__(self, product_model: ProductModel | None = None):
        self.product_model = product_model or ProductModel()

    def load_products_by_category(self, category_id: str):
        return self.product_model.list_products_by_category(category_id)

    def get_product(self, product_id: str):
        return self.product_model.get_product(product_id)

    def create_product(self, **fields):
        return self.product_model.create_product(**fields)

    def update_product(self, product_id: str, **fields):
        return self.product_model.update_product(product_id, **fields)

    def delete_product(self, product_id: str):
        return self.product_model.delete_product(product_id)
