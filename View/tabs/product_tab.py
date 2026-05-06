
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFileDialog,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

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


class Product_Tab(QWidget):
    def __init__(self):
        super().__init__()
        self.products = [
            {
                "id": 1,
                "name": "Classic Burger",
                "category": "Main Courses",
                "price": 210.00,
                "status": "Visible",
                "image": "burger.jpg",
                "description": "House burger with cheddar, pickles, and signature sauce.",
            },
            {
                "id": 2,
                "name": "Iced Latte",
                "category": "Drinks",
                "price": 88.00,
                "status": "Visible",
                "image": "iced-latte.jpg",
                "description": "Cold espresso, milk, and ice.",
            },
            {
                "id": 3,
                "name": "Chocolate Souffle",
                "category": "Desserts",
                "price": 130.00,
                "status": "Hidden",
                "image": "souffle.jpg",
                "description": "Warm chocolate souffle served with vanilla ice cream.",
            },
            {
                "id": 4,
                "name": "Caesar Salad",
                "category": "Starters",
                "price": 155.00,
                "status": "Visible",
                "image": "caesar.jpg",
                "description": "Romaine, parmesan, croutons, and grilled chicken.",
            },
        ]
        self.selected_product_id = None

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(18)

        add_button = make_button("Add Product", "primary")
        add_button.clicked.connect(self._start_new_product)
        root.addWidget(
            SectionHeader(
                "Product Management",
                "Create, edit, hide, and prepare products for image upload via API.",
                [add_button],
            )
        )

        summary = QHBoxLayout()
        summary.setSpacing(12)
        self.total_card = StatCard("Total products", "4", "Across all categories")
        self.visible_card = StatCard("Visible", "3", "Shown on QR menu", "green")
        self.hidden_card = StatCard("Hidden", "1", "Kept out of customer menu", "amber")
        summary.addWidget(self.total_card)
        summary.addWidget(self.visible_card)
        summary.addWidget(self.hidden_card)
        root.addLayout(summary)

        content = QSplitter(Qt.Horizontal)
        content.setChildrenCollapsible(False)
        content.addWidget(self._build_category_filter())
        content.addWidget(self._build_product_table())
        content.addWidget(self._build_editor())
        content.setSizes([210, 620, 350])
        root.addWidget(content, 1)

        self._refresh_categories()
        self._refresh_table()
        if self.table.rowCount():
            self.table.selectRow(0)
        else:
            self._start_new_product()

    def _build_category_filter(self):
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        layout.addWidget(make_label("Categories", "section-title"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search products")
        self.search_input.textChanged.connect(self._refresh_table)
        layout.addWidget(self.search_input)

        self.category_list = QListWidget()
        self.category_list.currentItemChanged.connect(self._refresh_table)
        layout.addWidget(self.category_list, 1)
        return card

    def _build_product_table(self):
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        toolbar = QHBoxLayout()
        toolbar.addWidget(make_label("Menu Items", "section-title"))
        toolbar.addStretch(1)
        self.table_hint = make_badge("API-ready CRUD", "accent")
        toolbar.addWidget(self.table_hint)
        layout.addLayout(toolbar)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Product", "Category", "Price", "Status", "Image"])
        set_table_defaults(self.table)
        self.table.itemSelectionChanged.connect(self._load_selected_product)
        layout.addWidget(self.table, 1)
        return card

    def _build_editor(self):
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        layout.addWidget(make_label("Product Details", "section-title"))

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignTop)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Product name")

        self.category_input = QComboBox()

        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 99999)
        self.price_input.setDecimals(2)
        self.price_input.setPrefix("$ ")

        self.status_input = QComboBox()
        self.status_input.addItems(["Visible", "Hidden"])

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Short customer-facing description")
        self.description_input.setFixedHeight(92)

        form.addRow("Name", self.name_input)
        form.addRow("Category", self.category_input)
        form.addRow("Price", self.price_input)
        form.addRow("Menu status", self.status_input)
        form.addRow("Description", self.description_input)
        layout.addLayout(form)

        image_card = make_card()
        image_layout = QVBoxLayout(image_card)
        image_layout.setContentsMargins(12, 12, 12, 12)
        image_layout.setSpacing(8)
        image_layout.addWidget(make_label("Product Image", "muted"))
        self.image_label = QLabel("No image selected")
        self.image_label.setWordWrap(True)
        self.image_label.setStyleSheet("color: #667585;")
        upload_button = make_button("Upload Image")
        upload_button.clicked.connect(self._choose_image)
        image_layout.addWidget(self.image_label)
        image_layout.addWidget(upload_button)
        layout.addWidget(image_card)

        actions = QHBoxLayout()
        save_button = make_button("Save Changes", "primary")
        save_button.clicked.connect(self._save_product)
        delete_button = make_button("Delete", "danger")
        delete_button.clicked.connect(self._delete_product)
        actions.addWidget(save_button)
        actions.addWidget(delete_button)
        layout.addLayout(actions)

        self.form_status = make_label("Select a row or add a new product.", "muted")
        self.form_status.setWordWrap(True)
        layout.addWidget(self.form_status)
        layout.addStretch(1)
        return card

    def _refresh_categories(self):
        selected = self.category_list.currentItem().text() if self.category_list.currentItem() else None
        self.category_list.blockSignals(True)
        self.category_list.clear()
        all_item = QListWidgetItem("All categories")
        self.category_list.addItem(all_item)
        for category in self._categories():
            count = sum(1 for product in self.products if product["category"] == category)
            self.category_list.addItem(QListWidgetItem(f"{category} ({count})"))
        matches = self.category_list.findItems(selected or "All categories", Qt.MatchExactly)
        self.category_list.setCurrentItem(matches[0] if matches else all_item)
        self.category_list.blockSignals(False)

        current_category = self.category_input.currentText()
        self.category_input.blockSignals(True)
        self.category_input.clear()
        self.category_input.addItems(self._categories())
        index = self.category_input.findText(current_category)
        if index >= 0:
            self.category_input.setCurrentIndex(index)
        self.category_input.blockSignals(False)

    def _categories(self):
        return sorted({product["category"] for product in self.products})

    def _selected_category_filter(self):
        item = self.category_list.currentItem()
        if not item or item.text() == "All categories":
            return None
        return item.text().split(" (", 1)[0]

    def _filtered_products(self):
        query = self.search_input.text().strip().lower()
        category = self._selected_category_filter()
        rows = []
        for product in self.products:
            if category and product["category"] != category:
                continue
            if query and query not in product["name"].lower() and query not in product["category"].lower():
                continue
            rows.append(product)
        return rows

    def _refresh_table(self):
        rows = self._filtered_products()
        self.table.setRowCount(0)
        for product in rows:
            row = self.table.rowCount()
            self.table.insertRow(row)
            name_item = QTableWidgetItem(product["name"])
            name_item.setData(Qt.UserRole, product["id"])
            self.table.setItem(row, 0, name_item)
            self.table.setItem(row, 1, QTableWidgetItem(product["category"]))
            self.table.setItem(row, 2, QTableWidgetItem(f"$ {product['price']:.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(product["status"]))
            self.table.setItem(row, 4, QTableWidgetItem(product["image"]))

        total = len(self.products)
        visible = sum(1 for product in self.products if product["status"] == "Visible")
        hidden = total - visible
        self.total_card.value_label.setText(str(total))
        self.visible_card.value_label.setText(str(visible))
        self.hidden_card.value_label.setText(str(hidden))

    def _load_selected_product(self):
        selected = self.table.selectedItems()
        if not selected:
            return
        product_id = self.table.item(selected[0].row(), 0).data(Qt.UserRole)
        product = self._product_by_id(product_id)
        if not product:
            return
        self.selected_product_id = product_id
        self.name_input.setText(product["name"])
        self.category_input.setCurrentText(product["category"])
        self.price_input.setValue(product["price"])
        self.status_input.setCurrentText(product["status"])
        self.description_input.setPlainText(product["description"])
        self.image_label.setText(product["image"])
        self.form_status.setText(f"Editing {product['name']}.")

    def _product_by_id(self, product_id):
        return next((product for product in self.products if product["id"] == product_id), None)

    def _start_new_product(self):
        self.selected_product_id = None
        self.table.clearSelection()
        self.name_input.clear()
        if self.category_input.count():
            self.category_input.setCurrentIndex(0)
        self.price_input.setValue(0)
        self.status_input.setCurrentText("Visible")
        self.description_input.clear()
        self.image_label.setText("No image selected")
        self.form_status.setText("Ready to add a new product.")

    def _choose_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Product Image",
            "",
            "Images (*.png *.jpg *.jpeg *.webp)",
        )
        if path:
            self.image_label.setText(path)

    def _save_product(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing product name", "Product name is required.")
            return

        payload = {
            "name": name,
            "category": self.category_input.currentText(),
            "price": float(self.price_input.value()),
            "status": self.status_input.currentText(),
            "image": self.image_label.text() if self.image_label.text() != "No image selected" else "pending-upload.jpg",
            "description": self.description_input.toPlainText().strip(),
        }

        if self.selected_product_id:
            product = self._product_by_id(self.selected_product_id)
            if product:
                product.update(payload)
                self.form_status.setText("Product changes saved locally. API PUT can be wired here.")
        else:
            payload["id"] = max(product["id"] for product in self.products) + 1 if self.products else 1
            self.products.append(payload)
            self.selected_product_id = payload["id"]
            self.form_status.setText("Product added locally. API POST can be wired here.")

        self._refresh_categories()
        self._refresh_table()

    def _delete_product(self):
        if not self.selected_product_id:
            self.form_status.setText("Select a product before deleting.")
            return
        product = self._product_by_id(self.selected_product_id)
        if not product:
            return
        self.products = [row for row in self.products if row["id"] != self.selected_product_id]
        self.form_status.setText(f"Deleted {product['name']} locally. API DELETE can be wired here.")
        self._refresh_categories()
        self._refresh_table()
        self._start_new_product()
