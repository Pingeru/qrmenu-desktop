"""Controller for category actions."""

from models.category_model import CategoryModel


class CategoryController:
    def __init__(self, category_model: CategoryModel | None = None):
        self.category_model = category_model or CategoryModel()

    def load_categories(self, business_id: str | None = None):
        return self.category_model.list_categories(business_id=business_id)

    def get_category(self, category_id: str):
        return self.category_model.get_category(category_id)

    def create_category(self, name: str):
        return self.category_model.create_category(name)

    def update_category(self, category_id: str, name: str):
        return self.category_model.update_category(category_id, name)

    def delete_category(self, category_id: str):
        return self.category_model.delete_category(category_id)
