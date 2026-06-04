from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
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
    QHeaderView,
    QSizePolicy,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from models.api_client import ApiError
from utils.config import API_BASE_URL

try:
    from view.components import (
        SectionHeader,
        StatCard,
        make_badge,
        make_button,
        make_card,
        make_label,
        make_scroll_area,
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
        make_scroll_area,
        set_table_defaults,
    )


class Product_Tab(QWidget):
    def __init__(self, product_controller=None, category_controller=None, auth_model=None):
        super().__init__()
        self.product_controller = product_controller
        self.category_controller = category_controller
        self.auth_model = auth_model
        self.products = []
        self.categories = []
        self.selected_product_id = None
        self.selected_image_path = None
        self.image_cache = {}
        self.backend_dirty = True

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        body = QWidget()
        root = QVBoxLayout(body)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(18)
        outer.addWidget(make_scroll_area(body), 1)

        self.add_button = make_button("Add Product", "primary")
        self.add_button.clicked.connect(self._start_new_product)
        refresh_button = make_button("Refresh")
        refresh_button.clicked.connect(self._load_backend_data)
        root.addWidget(
            SectionHeader(
                "Product Management",
                "Create and manage menu products through qrmenu-api product endpoints.",
                [refresh_button, self.add_button],
            )
        )

        summary = QHBoxLayout()
        summary.setSpacing(12)
        self.total_card = StatCard("Total products", "0", "Loaded from backend")
        self.visible_card = StatCard("Visible", "0", "Shown on QR menu", "green")
        self.hidden_card = StatCard("Hidden", "0", "Kept out of customer menu", "amber")
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

        self._set_controls_enabled()
        self._load_backend_data()

    def mark_backend_dirty(self):
        self.backend_dirty = True

    def refresh_from_backend(self):
        if self.backend_dirty:
            self._load_backend_data()

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
        self.table_hint = make_badge("API connected", "accent")
        toolbar.addWidget(self.table_hint)
        layout.addLayout(toolbar)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Product", "Category", "Price", "Status", "Image"])
        set_table_defaults(self.table)
        self.table.verticalHeader().setDefaultSectionSize(74)
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        self.table.setColumnWidth(4, 92)
        self.table.itemSelectionChanged.connect(self._load_selected_product)
        layout.addWidget(self.table, 1)
        return card

    def _build_editor(self):
        card = make_card()
        card.setMinimumWidth(300)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        layout.addWidget(make_label("Product Details", "section-title"))

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignTop)
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form.setRowWrapPolicy(QFormLayout.WrapLongRows)
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
        self.description_input.setMinimumHeight(72)
        self.description_input.setMaximumHeight(130)
        for field in [
            self.name_input,
            self.category_input,
            self.price_input,
            self.status_input,
            self.description_input,
        ]:
            field.setMinimumWidth(0)
            field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

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
        self.image_preview = QLabel("No image")
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setMinimumHeight(132)
        self.image_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.image_preview.setStyleSheet(
            "background: #f7faf9; border: 1px solid #d8e2df; border-radius: 6px; color: #65736f;"
        )
        self.image_label = QLabel("No image selected")
        self.image_label.setWordWrap(True)
        self.image_label.setStyleSheet("color: #667585;")
        self.upload_button = make_button("Upload Image")
        self.upload_button.clicked.connect(self._choose_image)
        image_layout.addWidget(self.image_preview)
        image_layout.addWidget(self.image_label)
        image_layout.addWidget(self.upload_button)
        layout.addWidget(image_card)

        actions = QHBoxLayout()
        self.save_button = make_button("Save Changes", "primary")
        self.save_button.clicked.connect(self._save_product)
        self.delete_button = make_button("Delete", "danger")
        self.delete_button.clicked.connect(self._delete_product)
        actions.addWidget(self.save_button)
        actions.addWidget(self.delete_button)
        layout.addLayout(actions)

        self.form_status = make_label("", "muted")
        self.form_status.setWordWrap(True)
        layout.addWidget(self.form_status)
        layout.addStretch(1)
        return make_scroll_area(card)

    def _load_backend_data(self):
        if not self.product_controller or not self.category_controller:
            self.products = []
            self.categories = []
            self.backend_dirty = False
            self.form_status.setText("Product endpoints are not connected in this app instance.")
            self._refresh_categories()
            self._refresh_table()
            self._start_new_product()
            return

        try:
            api_categories = self.category_controller.load_categories(self._business_id())
        except ApiError as exc:
            self.form_status.setText(f"Category sync failed: {exc}")
            return

        self.categories = [self._category_from_api(category) for category in api_categories]
        load_errors = []
        try:
            api_products = self.product_controller.load_products(business_id=self._business_id())
            self.products = [self._product_from_api(product) for product in api_products]
        except ApiError as exc:
            self.products = []
            load_errors.append(str(exc))

        if load_errors:
            load_errors = self._load_products_by_category_fallback()

        for product in self.products:
            product["category"] = self._category_name_by_id(product["category_id"])

        self.selected_product_id = None
        self.selected_image_path = None
        self._refresh_categories()
        self._refresh_table()
        self._set_controls_enabled()
        self.backend_dirty = False

        if load_errors:
            self.form_status.setText("Some product categories could not be loaded.")
        elif not self.categories:
            self.form_status.setText("Create a category before adding products.")
        elif not self.products:
            self.form_status.setText("No products found on backend.")
        else:
            self.form_status.setText("")

        if self.table.rowCount():
            self.table.selectRow(0)
        else:
            self._start_new_product()

    def _load_products_by_category_fallback(self):
        self.products = []
        load_errors = []
        for category in self.categories:
            try:
                api_products = self.product_controller.load_products_by_category(category["id"])
            except ApiError as exc:
                load_errors.append(f"{category['name']}: {exc}")
                continue
            self.products.extend(self._product_from_api(product) for product in api_products)
        return load_errors

    def _category_from_api(self, category):
        name = category.get("name") or "Unnamed category"
        return {
            "id": category.get("_id") or category.get("id"),
            "name": name,
        }

    def _business_id(self):
        business = self.auth_model.business if self.auth_model else None
        return business.get("_id") if business else None

    def _product_from_api(self, product):
        category_id = product.get("category_id")
        image_path = (
            product.get("image_path")
            or product.get("image_url")
            or product.get("image")
            or product.get("photo_url")
        )
        return {
            "id": product.get("_id") or product.get("id"),
            "name": product.get("name") or "",
            "category_id": category_id,
            "category": self._category_name_by_id(category_id),
            "price": float(product.get("price") or 0),
            "status": "Visible" if product.get("is_active", True) else "Hidden",
            "is_active": bool(product.get("is_active", True)),
            "description": product.get("description") or "",
            "image": self._image_display_text(image_path),
            "image_path": image_path,
        }

    def _category_name_by_id(self, category_id):
        category = next((item for item in self.categories if item["id"] == category_id), None)
        return category["name"] if category else "Unknown category"

    def _image_display_text(self, image_path):
        if not image_path:
            return "No image"
        path_text = str(image_path)
        parsed = urlparse(path_text)
        if parsed.scheme in {"http", "https"}:
            return Path(parsed.path).name or path_text
        path_obj = Path(path_text)
        return path_obj.name or path_text

    def _api_base_url(self):
        product_model = getattr(self.product_controller, "product_model", None)
        api_client = getattr(product_model, "api_client", None)
        return getattr(api_client, "base_url", API_BASE_URL).rstrip("/")

    def _image_url_candidates(self, image_path):
        path_text = str(image_path or "").strip()
        if not path_text:
            return []

        parsed = urlparse(path_text)
        if parsed.scheme in {"http", "https"}:
            return [path_text]

        api_base = self._api_base_url()
        api_parts = urlparse(api_base)
        if not api_parts.scheme or not api_parts.netloc:
            return []

        origin = f"{api_parts.scheme}://{api_parts.netloc}"
        normalized = path_text.lstrip("/")
        candidates = [
            urljoin(f"{origin}/", normalized),
            urljoin(f"{api_base}/", normalized),
        ]
        return list(dict.fromkeys(candidates))

    def _is_local_image_path(self, image_path):
        path_text = str(image_path or "").strip()
        if not path_text:
            return False
        if urlparse(path_text).scheme in {"http", "https"}:
            return False
        return Path(path_text).is_file()

    def _pixmap_for_image_path(self, image_path, width=140, height=100):
        path_text = str(image_path or "").strip()
        if not path_text:
            return QPixmap()

        cache_key = (path_text, width, height)
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]

        pixmap = QPixmap()
        local_path = Path(path_text)
        if local_path.is_file():
            pixmap.load(str(local_path))
        else:
            for url in self._image_url_candidates(path_text):
                try:
                    response = requests.get(url, timeout=3)
                except requests.RequestException:
                    continue
                if response.status_code >= 400:
                    continue
                if pixmap.loadFromData(response.content):
                    break

        if not pixmap.isNull():
            pixmap = pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_cache[cache_key] = pixmap
        return pixmap

    def _build_table_image_cell(self, image_path):
        preview = QLabel("-")
        preview.setAlignment(Qt.AlignCenter)
        preview.setMinimumHeight(64)
        preview.setStyleSheet("color: #65736f;")
        pixmap = self._pixmap_for_image_path(image_path, 76, 58)
        if not pixmap.isNull():
            preview.setPixmap(pixmap)
            preview.setToolTip(self._image_display_text(image_path))
        return preview

    def _set_image_preview(self, image_path):
        self.image_label.setText(self._image_display_text(image_path))
        pixmap = self._pixmap_for_image_path(image_path, 230, 132)
        if pixmap.isNull():
            self.image_preview.clear()
            self.image_preview.setText("No image")
            return
        self.image_preview.setText("")
        self.image_preview.setPixmap(pixmap)

    def _refresh_categories(self):
        selected = self.category_list.currentItem().text() if self.category_list.currentItem() else None
        self.category_list.blockSignals(True)
        self.category_list.clear()
        all_item = QListWidgetItem("All categories")
        self.category_list.addItem(all_item)
        for category in self.categories:
            count = sum(1 for product in self.products if product["category_id"] == category["id"])
            self.category_list.addItem(QListWidgetItem(f"{category['name']} ({count})"))
        matches = self.category_list.findItems(selected or "All categories", Qt.MatchExactly)
        self.category_list.setCurrentItem(matches[0] if matches else all_item)
        self.category_list.blockSignals(False)

        current_category_id = self.category_input.currentData()
        self.category_input.blockSignals(True)
        self.category_input.clear()
        for category in self.categories:
            self.category_input.addItem(category["name"], category["id"])
        index = self.category_input.findData(current_category_id)
        if index >= 0:
            self.category_input.setCurrentIndex(index)
        self.category_input.blockSignals(False)

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
            self.table.setItem(row, 4, QTableWidgetItem(""))
            self.table.setCellWidget(row, 4, self._build_table_image_cell(product["image_path"]))

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
        self.selected_image_path = product["image_path"] if self._is_local_image_path(product["image_path"]) else None
        self.name_input.setText(product["name"])
        self._set_category_input(product["category_id"])
        self.price_input.setValue(product["price"])
        self.status_input.setCurrentText(product["status"])
        self.description_input.setPlainText(product["description"])
        self._set_image_preview(product["image_path"])
        self.form_status.setText(f"Editing {product['name']}.")
        self._set_controls_enabled()

    def _set_category_input(self, category_id):
        index = self.category_input.findData(category_id)
        if index >= 0:
            self.category_input.setCurrentIndex(index)

    def _product_by_id(self, product_id):
        return next((product for product in self.products if product["id"] == product_id), None)

    def _start_new_product(self):
        self.selected_product_id = None
        self.selected_image_path = None
        self.table.clearSelection()
        self.name_input.clear()
        if self.category_input.count():
            self.category_input.setCurrentIndex(0)
        self.price_input.setValue(0)
        self.status_input.setCurrentText("Visible")
        self.description_input.clear()
        self._set_image_preview(None)
        self.image_label.setText("No image selected")
        if not self.categories:
            self.form_status.setText("Create a category before adding products.")
        else:
            self.form_status.setText("Ready to add a product.")
        self._set_controls_enabled()

    def _choose_image(self):
        if not self.product_controller:
            self.form_status.setText("Product image upload needs the product API.")
            return
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Product Image",
            "",
            "Images (*.png *.jpg *.jpeg *.webp)",
        )
        if path:
            self.selected_image_path = path
            self._set_image_preview(path)

    def _save_product(self):
        if not self.product_controller:
            QMessageBox.information(
                self,
                "Product endpoint pending",
                "Product data is not saved because the product API is not connected.",
            )
            return

        name = self.name_input.text().strip()
        category_id = self.category_input.currentData()
        if not name:
            QMessageBox.warning(self, "Missing product name", "Product name is required.")
            return
        if not category_id:
            QMessageBox.warning(self, "Missing category", "Create or select a category first.")
            return

        fields = {
            "name": name,
            "category_id": category_id,
            "price": float(self.price_input.value()),
            "description": self.description_input.toPlainText().strip(),
            "is_active": self.status_input.currentText() == "Visible",
            "image_path": self.selected_image_path,
        }

        try:
            if self.selected_product_id:
                saved_product = self.product_controller.update_product(self.selected_product_id, **fields)
                status_text = "Product changes saved to backend."
            else:
                saved_product = self.product_controller.create_product(**fields)
                status_text = "Product added to backend."
        except ApiError as exc:
            QMessageBox.warning(self, "Product save failed", str(exc))
            return

        saved_product_id = saved_product.get("_id") or saved_product.get("id")
        self._load_backend_data()
        self._select_product(saved_product_id)
        self.form_status.setText(status_text)

    def _delete_product(self):
        if not self.selected_product_id:
            self.form_status.setText("Select a product before deleting.")
            return

        product = self._product_by_id(self.selected_product_id)
        product_name = product["name"] if product else "this product"
        choice = QMessageBox.question(
            self,
            "Delete product",
            f"Delete {product_name} from qrmenu-api?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if choice != QMessageBox.Yes:
            return

        try:
            self.product_controller.delete_product(self.selected_product_id)
        except ApiError as exc:
            QMessageBox.warning(self, "Product delete failed", str(exc))
            return

        self._load_backend_data()
        self.form_status.setText(f"Deleted {product_name} from backend.")

    def _select_product(self, product_id):
        if not product_id:
            return
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.data(Qt.UserRole) == product_id:
                self.table.selectRow(row)
                return

    def _set_controls_enabled(self):
        connected = bool(self.product_controller and self.category_controller)
        has_categories = bool(self.categories)
        self.add_button.setEnabled(connected and has_categories)
        self.save_button.setEnabled(connected and has_categories)
        self.upload_button.setEnabled(connected and has_categories)
        self.delete_button.setEnabled(connected and bool(self.selected_product_id))
        if not connected:
            self.add_button.setToolTip("Product endpoints are not connected.")
            self.save_button.setToolTip("Product endpoints are not connected.")
            self.upload_button.setToolTip("Product endpoints are not connected.")
            self.delete_button.setToolTip("Product endpoints are not connected.")
        elif not has_categories:
            self.add_button.setToolTip("Create a category before adding products.")
            self.save_button.setToolTip("Create a category before saving products.")
            self.upload_button.setToolTip("Create a category before uploading product images.")
            self.delete_button.setToolTip("Select a product before deleting.")
        else:
            self.add_button.setToolTip("Create a new backend product.")
            self.save_button.setToolTip("Save product to qrmenu-api.")
            self.upload_button.setToolTip("Attach an image to the next product save.")
            self.delete_button.setToolTip("Delete selected product from qrmenu-api.")
