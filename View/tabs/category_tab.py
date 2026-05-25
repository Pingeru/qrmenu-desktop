
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QAbstractItemView,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from models.api_client import ApiError

try:
    from view.components import (
        SectionHeader,
        StatCard,
        make_badge,
        make_button,
        make_card,
        make_label,
        set_table_defaults,
    )
except ModuleNotFoundError:
    from components import (
        SectionHeader,
        StatCard,
        make_badge,
        make_button,
        make_card,
        make_label,
        set_table_defaults,
    )


class Catagory_Tab(QWidget):
    def __init__(self, category_controller=None, auth_model=None, on_categories_changed=None):
        super().__init__()
        self.category_controller = category_controller
        self.auth_model = auth_model
        self.on_categories_changed = on_categories_changed
        if self.category_controller:
            self.categories = []
            self.product_map = {}
        else:
            self.categories = [
                {"id": 1, "name": "Starters", "slug": "starters", "order": 1, "status": "Visible"},
                {"id": 2, "name": "Main Courses", "slug": "main-courses", "order": 2, "status": "Visible"},
                {"id": 3, "name": "Desserts", "slug": "desserts", "order": 3, "status": "Visible"},
                {"id": 4, "name": "Drinks", "slug": "drinks", "order": 4, "status": "Visible"},
            ]
            self.product_map = {
                "Starters": ["Caesar Salad", "Soup of the Day"],
                "Main Courses": ["Classic Burger", "Grilled Chicken"],
                "Desserts": ["Chocolate Souffle", "Tiramisu"],
                "Drinks": ["Iced Latte", "Fresh Lemonade", "Sparkling Water"],
            }
        self.selected_category_id = None
        self.editor_mode = "create"

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(18)

        add_button = make_button("Add Category", "primary")
        add_button.clicked.connect(self._start_new_category)
        refresh_button = make_button("Refresh")
        refresh_button.clicked.connect(self._load_categories)
        root.addWidget(
            SectionHeader(
                "Category Management",
                "Create menu sections, control visibility, and keep product assignments tidy.",
                [refresh_button, add_button],
            )
        )

        summary = QHBoxLayout()
        summary.setSpacing(12)
        self.total_card = StatCard("Categories", "4", "Menu sections")
        self.visible_card = StatCard("Visible", "4", "Shown to customers", "green")
        self.assigned_card = StatCard("Assigned products", "9", "Across visible sections", "blue")
        summary.addWidget(self.total_card)
        summary.addWidget(self.visible_card)
        summary.addWidget(self.assigned_card)
        root.addLayout(summary)

        content = QHBoxLayout()
        content.setSpacing(16)
        content.addWidget(self._build_table(), 3)
        content.addWidget(self._build_editor(), 2)
        root.addLayout(content, 1)

        if self.category_controller:
            self._load_categories()
        else:
            self._refresh_table()
            if self.table.rowCount():
                self.table.selectRow(0)
            else:
                self._start_new_category()

    def _build_table(self):
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        toolbar = QHBoxLayout()
        toolbar.addWidget(make_label("Menu Categories", "section-title"))
        toolbar.addStretch(1)
        toolbar.addWidget(make_badge("CRUD endpoints", "accent"))
        layout.addLayout(toolbar)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Order", "Category", "Slug", "Products", "Status"])
        set_table_defaults(self.table)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self._load_selected_category)
        layout.addWidget(self.table, 1)
        return card

    def _build_editor(self):
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        layout.addWidget(make_label("Category Details", "section-title"))

        form = QFormLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Category name")
        self.slug_input = QLineEdit()
        self.slug_input.setPlaceholderText("category-slug")
        self.order_input = QSpinBox()
        self.order_input.setRange(1, 99)
        self.status_input = QComboBox()
        self.status_input.addItems(["Visible", "Hidden"])

        form.addRow("Name", self.name_input)
        form.addRow("Slug", self.slug_input)
        form.addRow("Menu order", self.order_input)
        form.addRow("Status", self.status_input)
        layout.addLayout(form)

        layout.addWidget(make_label("Assigned Products", "section-title"))
        self.assigned_products = QListWidget()
        layout.addWidget(self.assigned_products, 1)

        actions = QHBoxLayout()
        self.save_button = make_button("Add Category", "primary")
        self.save_button.clicked.connect(self._save_category)
        self.delete_button = make_button("Delete", "danger")
        self.delete_button.clicked.connect(self._delete_category)
        actions.addWidget(self.save_button)
        actions.addWidget(self.delete_button)
        layout.addLayout(actions)

        self.form_status = make_label("Select a category or create a new one.", "muted")
        self.form_status.setWordWrap(True)
        layout.addWidget(self.form_status)
        return card

    def _load_categories(self):
        if not self.category_controller:
            self._refresh_table()
            return

        try:
            api_categories = self.category_controller.load_categories(self._business_id())
        except ApiError as exc:
            self.form_status.setText(f"Backend sync failed: {exc}")
            return

        previous_product_map = self.product_map
        self.categories = [
            self._category_from_api(category, index + 1)
            for index, category in enumerate(api_categories)
        ]
        self.product_map = {
            category["name"]: previous_product_map.get(category["name"], [])
            for category in self.categories
        }
        self.selected_category_id = None
        self._refresh_table()
        if self.table.rowCount():
            self.table.selectRow(0)
            self.form_status.setText("Categories loaded from backend.")
        else:
            self._start_new_category()
            self.form_status.setText("No categories found on backend.")

    def _business_id(self):
        business = self.auth_model.business if self.auth_model else None
        return business.get("_id") if business else None

    def _category_from_api(self, category, order):
        name = category.get("name", "")
        return {
            "id": category.get("_id") or category.get("id"),
            "name": name,
            "slug": self._slug_for(name),
            "order": order,
            "status": "Visible",
            "business_id": category.get("business_id"),
            "created_at": category.get("created_at"),
        }

    def _slug_for(self, value):
        return value.strip().lower().replace(" ", "-")

    def _refresh_table(self):
        self.categories.sort(key=lambda item: item["order"])
        was_blocked = self.table.blockSignals(True)
        self.table.setRowCount(0)
        for category in self.categories:
            row = self.table.rowCount()
            self.table.insertRow(row)
            order_item = QTableWidgetItem(str(category["order"]))
            order_item.setData(Qt.UserRole, category["id"])
            self.table.setItem(row, 0, order_item)
            self.table.setItem(row, 1, QTableWidgetItem(category["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(category["slug"]))
            self.table.setItem(row, 3, QTableWidgetItem(str(len(self.product_map.get(category["name"], [])))))
            self.table.setItem(row, 4, QTableWidgetItem(category["status"]))
        self.table.blockSignals(was_blocked)

        visible = sum(1 for category in self.categories if category["status"] == "Visible")
        assigned = sum(len(products) for products in self.product_map.values())
        self.total_card.value_label.setText(str(len(self.categories)))
        self.visible_card.value_label.setText(str(visible))
        self.assigned_card.value_label.setText(str(assigned))

    def _load_selected_category(self):
        selected = self.table.selectedItems()
        if not selected:
            return
        category_id = self.table.item(selected[0].row(), 0).data(Qt.UserRole)
        category = self._category_by_id(category_id)
        if not category:
            return
        self._set_editor_mode("edit")
        self.selected_category_id = category_id
        self.name_input.setText(category["name"])
        self.slug_input.setText(category["slug"])
        self.order_input.setValue(category["order"])
        self.status_input.setCurrentText(category["status"])
        self._refresh_assigned_products(category["name"])
        self.form_status.setText(f"Editing {category['name']}.")

    def _refresh_assigned_products(self, category_name):
        self.assigned_products.clear()
        products = self.product_map.get(category_name, [])
        if not products:
            self.assigned_products.addItem("No products assigned yet.")
            return
        for product in products:
            self.assigned_products.addItem(product)

    def _category_by_id(self, category_id):
        return next((category for category in self.categories if category["id"] == category_id), None)

    def _start_new_category(self):
        self._set_editor_mode("create")
        self.selected_category_id = None
        was_blocked = self.table.blockSignals(True)
        self.table.clearSelection()
        self.table.blockSignals(was_blocked)
        self.name_input.clear()
        self.slug_input.clear()
        self.order_input.setValue(len(self.categories) + 1)
        self.status_input.setCurrentText("Visible")
        self.assigned_products.clear()
        self.assigned_products.addItem("Products can be assigned after category creation.")
        self.form_status.setText("Ready to add a category.")

    def _set_editor_mode(self, mode):
        self.editor_mode = mode
        if not hasattr(self, "save_button"):
            return
        if mode == "edit":
            self.save_button.setText("Save Changes")
            self.delete_button.setEnabled(True)
            self.delete_button.setToolTip("Delete the selected category.")
        else:
            self.save_button.setText("Add Category")
            self.delete_button.setEnabled(False)
            self.delete_button.setToolTip("Select a category from the table before deleting.")

    def _save_category(self):
        name = self.name_input.text().strip()
        slug = self.slug_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing category name", "Category name is required.")
            return
        if not slug:
            slug = self._slug_for(name)

        payload = {
            "name": name,
            "slug": slug,
            "order": int(self.order_input.value()),
            "status": self.status_input.currentText(),
        }

        if self.editor_mode == "edit" and self.selected_category_id:
            category = self._category_by_id(self.selected_category_id)
            if category:
                old_name = category["name"]
                if self.category_controller:
                    try:
                        api_category = self.category_controller.update_category(self.selected_category_id, name)
                    except ApiError as exc:
                        QMessageBox.warning(self, "Category update failed", str(exc))
                        return
                    payload.update(self._category_from_api(api_category, payload["order"]))
                    payload["slug"] = slug
                    payload["status"] = self.status_input.currentText()
                category.update(payload)
                if old_name != name:
                    self.product_map[name] = self.product_map.pop(old_name, [])
                status_text = "Category changes saved to backend." if self.category_controller else "Category changes saved locally."
                self.form_status.setText(status_text)
                self._refresh_table()
                self._refresh_assigned_products(name)
                self._notify_categories_changed()
            else:
                self._set_editor_mode("create")
                self.selected_category_id = None
                self._create_category(payload, name, slug)
        else:
            self._create_category(payload, name, slug)

    def _create_category(self, payload, name, slug):
        if self.category_controller:
            try:
                api_category = self.category_controller.create_category(name)
            except ApiError as exc:
                QMessageBox.warning(self, "Category create failed", str(exc))
                return
            payload.update(self._category_from_api(api_category, len(self.categories) + 1))
            payload["slug"] = slug
            payload["status"] = self.status_input.currentText()
        else:
            payload["id"] = max(category["id"] for category in self.categories) + 1 if self.categories else 1
        self.categories.append(payload)
        self.product_map.setdefault(name, [])
        status_text = "Category added to backend." if self.category_controller else "Category added locally."
        self._refresh_table()
        self._start_new_category()
        self.form_status.setText(status_text)
        self._notify_categories_changed()

    def _delete_category(self):
        if not self.selected_category_id:
            self.form_status.setText("Select a category before deleting.")
            return
        category = self._category_by_id(self.selected_category_id)
        if not category:
            return
        if self.product_map.get(category["name"]):
            QMessageBox.warning(
                self,
                "Category has products",
                "Move or remove assigned products before deleting this category.",
            )
            return
        if self.category_controller:
            try:
                self.category_controller.delete_category(self.selected_category_id)
            except ApiError as exc:
                QMessageBox.warning(self, "Category delete failed", str(exc))
                return
        self.categories = [row for row in self.categories if row["id"] != self.selected_category_id]
        status_text = "from backend" if self.category_controller else "locally"
        self.form_status.setText(f"Deleted {category['name']} {status_text}.")
        self._refresh_table()
        self._start_new_category()
        self._notify_categories_changed()

    def _notify_categories_changed(self):
        if self.on_categories_changed:
            self.on_categories_changed()


Category_Tab = Catagory_Tab
