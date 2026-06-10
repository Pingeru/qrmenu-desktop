import datetime as dt

from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QListWidget,
    QMessageBox,
    QStackedLayout,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from models.api_client import ApiError

try:
    from view.components import (
        COLORS,
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
        COLORS,
        SectionHeader,
        StatCard,
        make_badge,
        make_button,
        make_card,
        make_label,
        set_table_defaults,
    )


# Backend only supports these statuses (see API_DOCUMENTATION.md - Business Orders).
BACKEND_TO_UI_STATUS = {
    "placed": "Pending",
    "preparing": "Preparing",
    "ready": "Ready",
    "cancelled": "Cancelled",
}
UI_TO_BACKEND_STATUS = {value: key for key, value in BACKEND_TO_UI_STATUS.items()}
STATUS_TONES = {
    "Pending": "amber",
    "Preparing": "blue",
    "Ready": "green",
    "Cancelled": "red",
}
STATUS_ORDER = ["Pending", "Preparing", "Ready", "Cancelled"]


def _format_money(value):
    try:
        return f"$ {float(value or 0):,.2f}"
    except (TypeError, ValueError):
        return "$ 0.00"


class Order_Tab(QWidget):
    def __init__(self, order_controller=None):
        super().__init__()
        self.order_controller = order_controller
        self.orders = []
        self.selected_order_id = None
        self.status_buttons = []

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(16)

        refresh_button = make_button("Refresh", "primary")
        refresh_button.setToolTip("Load live business orders from qrmenu-api.")
        refresh_button.clicked.connect(lambda: self._load_backend_orders(show_error=True))
        root.addWidget(
            SectionHeader(
                "Live Order Queue",
                "Orders streamed from qrmenu-api business endpoints.",
                [refresh_button],
            )
        )

        summary = QHBoxLayout()
        summary.setSpacing(12)
        self.pending_card = StatCard("Pending", "0", "New customer orders", "amber")
        self.preparing_card = StatCard("Preparing", "0", "In kitchen", "blue")
        self.ready_card = StatCard("Ready", "0", "Awaiting pickup", "green")
        self.cancelled_card = StatCard("Cancelled", "0", "Removed from flow", "red")
        summary.addWidget(self.pending_card)
        summary.addWidget(self.preparing_card)
        summary.addWidget(self.ready_card)
        summary.addWidget(self.cancelled_card)
        root.addLayout(summary)

        content = QHBoxLayout()
        content.setSpacing(16)
        content.addWidget(self._build_queue(), 3)
        content.addWidget(self._build_detail_panel(), 2)
        root.addLayout(content, 1)

        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: self._load_backend_orders(show_error=False))
        self.timer.start(30000)

        self._load_backend_orders(show_error=False)

    # ---------- UI builders ----------

    def _build_queue(self):
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        toolbar.addWidget(make_label("Orders", "section-title"))
        toolbar.addStretch(1)
        toolbar.addWidget(make_label("Filter", "muted"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All"] + STATUS_ORDER)
        self.status_filter.setMinimumWidth(130)
        self.status_filter.currentTextChanged.connect(self._refresh_table)
        toolbar.addWidget(self.status_filter)
        layout.addLayout(toolbar)

        # Stacked area: table OR empty state
        self.queue_stack = QStackedLayout()
        self.queue_stack.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["Order", "Time", "Items", "Total", "Status", "Customer"]
        )
        set_table_defaults(self.table)
        self.table.itemSelectionChanged.connect(self._load_selected_order)

        self.empty_state = self._build_empty_state(
            "No live orders right now.",
            "New orders from your menu will appear here automatically.",
        )

        stack_holder = QWidget()
        stack_holder.setLayout(self.queue_stack)
        self.queue_stack.addWidget(self.table)
        self.queue_stack.addWidget(self.empty_state)
        layout.addWidget(stack_holder, 1)

        self.sync_label = make_label("Last sync: waiting for qrmenu-api", "muted")
        layout.addWidget(self.sync_label)
        return card

    def _build_empty_state(self, title, subtitle):
        wrapper = QWidget()
        v = QVBoxLayout(wrapper)
        v.setContentsMargins(20, 40, 20, 40)
        v.setSpacing(6)
        v.addStretch(1)

        title_label = make_label(title)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"color: {COLORS['text']};")
        v.addWidget(title_label)

        subtitle_label = make_label(subtitle, "muted")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setWordWrap(True)
        v.addWidget(subtitle_label)
        v.addStretch(1)
        return wrapper

    def _build_detail_panel(self):
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        layout.addWidget(make_label("Order Details", "section-title"))

        self.order_title = make_label("No order selected", "title")
        layout.addWidget(self.order_title)

        self.order_meta = make_label(
            "Select a row from the queue to see customer, items and totals.",
            "subtitle",
        )
        self.order_meta.setWordWrap(True)
        layout.addWidget(self.order_meta)

        self.status_badge_holder = QHBoxLayout()
        self.status_badge_holder.setContentsMargins(0, 4, 0, 4)
        self.status_badge_holder.addWidget(make_badge("No status", "neutral"))
        self.status_badge_holder.addStretch(1)
        layout.addLayout(self.status_badge_holder)

        layout.addWidget(make_label("Items", "section-title"))
        self.item_list = QListWidget()
        self.item_list.setMinimumHeight(160)
        layout.addWidget(self.item_list, 1)

        layout.addWidget(make_label("Update Status", "section-title"))
        status_actions = QHBoxLayout()
        status_actions.setSpacing(8)
        for status in STATUS_ORDER:
            variant = "primary" if status == "Ready" else "default"
            button = make_button(status, variant)
            button.setEnabled(False)
            button.clicked.connect(
                lambda checked=False, value=status: self._set_status(value)
            )
            self.status_buttons.append(button)
            status_actions.addWidget(button)
        layout.addLayout(status_actions)

        self.detail_status = make_label("", "muted")
        self.detail_status.setWordWrap(True)
        layout.addWidget(self.detail_status)
        return card

    # ---------- Data load ----------

    def _load_backend_orders(self, show_error=False):
        if not self.order_controller:
            self.orders = []
            self._refresh_table()
            self.sync_label.setText("Order controller is not connected.")
            return

        try:
            api_orders = self.order_controller.load_orders()
        except ApiError as exc:
            self.sync_label.setText(f"Order sync failed: {exc}")
            if hasattr(self, "detail_status"):
                self.detail_status.setText("Could not load live orders from qrmenu-api.")
            if show_error:
                QMessageBox.warning(self, "Order sync failed", str(exc))
            return

        selected_id = self.selected_order_id
        self.orders = [self._order_from_api(order) for order in (api_orders or [])]
        if selected_id and not self._order_by_id(selected_id):
            self.selected_order_id = None
        self._refresh_table()
        timestamp = QDateTime.currentDateTime().toString("HH:mm:ss")
        self.sync_label.setText(
            f"Last sync {timestamp}  -  {len(self.orders)} orders"
        )

    def _order_from_api(self, order):
        order = order or {}
        order_id = str(order.get("_id") or order.get("id") or "")
        short_id = order.get("short_order_id") or (order_id[-8:] if order_id else "-")
        status = BACKEND_TO_UI_STATUS.get(str(order.get("status") or "").lower(), "Pending")
        created_at = order.get("created_at") or ""
        items = [self._item_label(item) for item in (order.get("items") or [])]
        return {
            "id": order_id,
            "display_id": str(short_id),
            "created_at": created_at,
            "time": self._format_time(created_at),
            "items": items,
            "item_count": len(items),
            "total": self._to_float(order.get("total_amount")),
            "status": status,
            "source": self._customer_label(order.get("customer"), order.get("user_id")),
        }

    def _item_label(self, item):
        item = item or {}
        product_id = str(item.get("product_id") or "unknown")
        product_name = (item.get("product_name") or "").strip()
        quantity = int(item.get("quantity") or 0)
        if quantity <= 0:
            quantity = 1
        price = self._to_float(item.get("price_at_purchase"))
        label = product_name or f"Product {product_id[-6:]}"
        return f"{quantity} x {label}  -  {_format_money(price)}"

    def _customer_label(self, customer, user_id):
        if isinstance(customer, dict):
            name = (customer.get("name") or "").strip()
            phone = (customer.get("phone") or "").strip()
            if name and phone:
                return f"{name} - {phone}"
            if name:
                return name
            if phone:
                return phone
            customer_id = customer.get("id")
            if customer_id:
                return f"Client {str(customer_id)[-6:]}"
        if not user_id:
            return "Client"
        return f"Client {str(user_id)[-6:]}"

    def _format_time(self, value):
        parsed = self._parse_datetime(value)
        if parsed:
            return parsed.strftime("%H:%M")
        return str(value)[:16] if value else "-"

    def _parse_datetime(self, value):
        if not value:
            return None
        if isinstance(value, dt.datetime):
            return value
        text = str(value).replace("Z", "+00:00")
        try:
            return dt.datetime.fromisoformat(text)
        except ValueError:
            return None

    def _to_float(self, value):
        try:
            return float(value or 0)
        except (TypeError, ValueError):
            return 0.0

    # ---------- Rendering ----------

    def _refresh_table(self, *args):
        selected_status = (
            self.status_filter.currentText()
            if hasattr(self, "status_filter")
            else "All"
        )
        filtered = [
            order
            for order in self.orders
            if selected_status == "All" or order["status"] == selected_status
        ]

        self.table.blockSignals(True)
        self.table.setRowCount(0)
        for order in filtered:
            row = self.table.rowCount()
            self.table.insertRow(row)
            id_item = QTableWidgetItem(order["display_id"])
            id_item.setData(Qt.UserRole, order["id"])
            self.table.setItem(row, 0, id_item)
            self.table.setItem(row, 1, QTableWidgetItem(order["time"]))

            items_item = QTableWidgetItem(str(order["item_count"]))
            items_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, items_item)

            total_item = QTableWidgetItem(_format_money(order["total"]))
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 3, total_item)

            self.table.setItem(row, 4, QTableWidgetItem(order["status"]))
            self.table.setItem(row, 5, QTableWidgetItem(order["source"]))
        self.table.blockSignals(False)

        self._refresh_summary()

        # Toggle empty state vs table
        if filtered:
            self.queue_stack.setCurrentWidget(self.table)
            if self.selected_order_id and self._select_order(self.selected_order_id):
                return
            self.table.selectRow(0)
        else:
            self.queue_stack.setCurrentWidget(self.empty_state)
            self._clear_detail_panel()

    def _clear_detail_panel(self):
        self.selected_order_id = None
        if not hasattr(self, "order_title"):
            return
        self.order_title.setText("No order selected")
        self.order_meta.setText(
            "Select a row from the queue to see customer, items and totals."
        )
        self._set_status_badge("No status", "neutral")
        self.item_list.clear()
        self.detail_status.setText("")
        self._refresh_action_state()

    def _refresh_summary(self):
        counts = {status: 0 for status in STATUS_ORDER}
        for order in self.orders:
            if order["status"] in counts:
                counts[order["status"]] += 1
        self.pending_card.value_label.setText(str(counts["Pending"]))
        self.preparing_card.value_label.setText(str(counts["Preparing"]))
        self.ready_card.value_label.setText(str(counts["Ready"]))
        self.cancelled_card.value_label.setText(str(counts["Cancelled"]))

    def _load_selected_order(self):
        selected = self.table.selectedItems()
        if not selected:
            return
        order_id = self.table.item(selected[0].row(), 0).data(Qt.UserRole)
        order = self._order_by_id(order_id)
        if not order:
            return
        self.selected_order_id = order_id
        self.order_title.setText(f"Order {order['display_id']}")
        self.order_meta.setText(
            f"{order['source']}\n{order['time']}  -  Total {_format_money(order['total'])}"
        )
        self._set_status_badge(order["status"], STATUS_TONES.get(order["status"], "neutral"))
        self.item_list.clear()
        if order["items"]:
            for item in order["items"]:
                self.item_list.addItem(item)
        else:
            self.item_list.addItem("No item details returned.")
        self.detail_status.setText("")
        self._refresh_action_state()

    def _set_status_badge(self, status, tone="neutral"):
        while self.status_badge_holder.count():
            child = self.status_badge_holder.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.status_badge_holder.addWidget(make_badge(status, tone))
        self.status_badge_holder.addStretch(1)

    def _set_status(self, status):
        if not self.selected_order_id or not self.order_controller:
            self.detail_status.setText("Select an order before updating status.")
            return

        backend_status = UI_TO_BACKEND_STATUS[status]
        try:
            self.order_controller.update_order_status(self.selected_order_id, backend_status)
        except ApiError as exc:
            QMessageBox.warning(self, "Order update failed", str(exc))
            return

        updated_order_id = self.selected_order_id
        self._load_backend_orders(show_error=False)
        self._select_order(updated_order_id)
        self.detail_status.setText(f"Order status saved as {status}.")

    def _refresh_action_state(self):
        enabled = bool(self.selected_order_id and self.order_controller)
        for button in self.status_buttons:
            button.setEnabled(enabled)

    def _select_order(self, order_id):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.data(Qt.UserRole) == order_id:
                self.table.selectRow(row)
                return True
        return False

    def _order_by_id(self, order_id):
        return next((order for order in self.orders if order["id"] == order_id), None)
