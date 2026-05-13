
from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QTableWidget,
    QTableWidgetItem,
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


class Order_Tab(QWidget):
    def __init__(self):
        super().__init__()
        self.orders = []
        self.selected_order_id = None

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(18)

        refresh_button = make_button("Refresh")
        refresh_button.setToolTip("Order endpoints are not available in the backend yet.")
        refresh_button.clicked.connect(self._refresh_orders)
        root.addWidget(
            SectionHeader(
                "Live Order Queue",
                "Order endpoints are not available yet; this view will stay empty until the backend is ready.",
                [refresh_button],
            )
        )

        summary = QHBoxLayout()
        summary.setSpacing(12)
        self.pending_card = StatCard("Pending", "0", "Needs attention", "amber")
        self.preparing_card = StatCard("Preparing", "0", "In kitchen", "blue")
        self.ready_card = StatCard("Ready", "0", "Awaiting pickup", "green")
        self.completed_card = StatCard("Completed", "0", "Closed in this session")
        summary.addWidget(self.pending_card)
        summary.addWidget(self.preparing_card)
        summary.addWidget(self.ready_card)
        summary.addWidget(self.completed_card)
        root.addLayout(summary)

        content = QHBoxLayout()
        content.setSpacing(16)
        content.addWidget(self._build_queue(), 3)
        content.addWidget(self._build_detail_panel(), 2)
        root.addLayout(content, 1)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_sync_label)
        self.timer.start(30000)

        self._refresh_orders()
        if self.table.rowCount():
            self.table.selectRow(0)

    def _build_queue(self):
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        toolbar = QHBoxLayout()
        toolbar.addWidget(make_label("Orders", "section-title"))
        toolbar.addStretch(1)
        toolbar.addWidget(make_badge("Awaiting API", "neutral"))
        toolbar.addWidget(make_label("Filter", "muted"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Pending", "Preparing", "Ready", "Completed"])
        self.status_filter.currentTextChanged.connect(self._refresh_orders)
        toolbar.addWidget(self.status_filter)
        layout.addLayout(toolbar)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Order ID", "Time", "Items", "Total", "Status", "Source"])
        set_table_defaults(self.table)
        self.table.itemSelectionChanged.connect(self._load_selected_order)
        layout.addWidget(self.table, 1)

        self.sync_label = make_label("Last sync: awaiting order API", "muted")
        layout.addWidget(self.sync_label)
        return card

    def _build_detail_panel(self):
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        layout.addWidget(make_label("Order Details", "section-title"))
        self.order_title = make_label("Select an order", "title")
        layout.addWidget(self.order_title)

        self.order_meta = make_label("No order selected.", "subtitle")
        self.order_meta.setWordWrap(True)
        layout.addWidget(self.order_meta)

        self.status_badge_holder = QHBoxLayout()
        self.status_badge_holder.addWidget(make_badge("No status", "neutral"))
        self.status_badge_holder.addStretch(1)
        layout.addLayout(self.status_badge_holder)

        layout.addWidget(make_label("Items", "section-title"))
        self.item_list = QListWidget()
        layout.addWidget(self.item_list, 1)

        layout.addWidget(make_label("Update Status", "section-title"))
        status_actions = QHBoxLayout()
        for status in ["Pending", "Preparing", "Ready", "Completed"]:
            button = make_button(status)
            button.setEnabled(False)
            button.setToolTip("Order status updates are disabled until backend order endpoints exist.")
            button.clicked.connect(lambda checked=False, value=status: self._set_status(value))
            status_actions.addWidget(button)
        layout.addLayout(status_actions)

        self.detail_status = make_label("Order status updates are disabled until backend order endpoints exist.", "muted")
        self.detail_status.setWordWrap(True)
        layout.addWidget(self.detail_status)
        return card

    def _refresh_orders(self):
        selected_status = self.status_filter.currentText() if hasattr(self, "status_filter") else "All"
        filtered = [
            order
            for order in self.orders
            if selected_status == "All" or order["status"] == selected_status
        ]
        self.table.setRowCount(0)
        for order in filtered:
            row = self.table.rowCount()
            self.table.insertRow(row)
            id_item = QTableWidgetItem(order["id"])
            id_item.setData(Qt.UserRole, order["id"])
            self.table.setItem(row, 0, id_item)
            self.table.setItem(row, 1, QTableWidgetItem(order["time"]))
            self.table.setItem(row, 2, QTableWidgetItem(", ".join(order["items"])))
            self.table.setItem(row, 3, QTableWidgetItem(f"$ {order['total']:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(order["status"]))
            self.table.setItem(row, 5, QTableWidgetItem(order["source"]))

        self._refresh_summary()
        if not filtered:
            self._clear_detail_panel()
        self._update_sync_label()

    def _clear_detail_panel(self):
        self.selected_order_id = None
        if hasattr(self, "order_title"):
            self.order_title.setText("No orders")
            self.order_meta.setText("No order data is loaded because the backend does not expose order endpoints yet.")
            self._set_status_badge("No status")
            self.item_list.clear()
            self.detail_status.setText("Waiting for backend order endpoints.")

    def _refresh_summary(self):
        counts = {status: 0 for status in ["Pending", "Preparing", "Ready", "Completed"]}
        for order in self.orders:
            counts[order["status"]] += 1
        self.pending_card.value_label.setText(str(counts["Pending"]))
        self.preparing_card.value_label.setText(str(counts["Preparing"]))
        self.ready_card.value_label.setText(str(counts["Ready"]))
        self.completed_card.value_label.setText(str(counts["Completed"]))

    def _load_selected_order(self):
        selected = self.table.selectedItems()
        if not selected:
            return
        order_id = self.table.item(selected[0].row(), 0).data(Qt.UserRole)
        order = self._order_by_id(order_id)
        if not order:
            return
        self.selected_order_id = order_id
        self.order_title.setText(order["id"])
        self.order_meta.setText(
            f"{order['source']} - {order['time']} - Total $ {order['total']:.2f}"
        )
        self._set_status_badge(order["status"])
        self.item_list.clear()
        for item in order["items"]:
            self.item_list.addItem(item)
        self.detail_status.setText("Ready to send PUT /orders/{id}/status when API is connected.")

    def _set_status_badge(self, status):
        while self.status_badge_holder.count():
            child = self.status_badge_holder.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        tone = {
            "Pending": "amber",
            "Preparing": "blue",
            "Ready": "green",
            "Completed": "neutral",
        }.get(status, "neutral")
        self.status_badge_holder.addWidget(make_badge(status, tone))
        self.status_badge_holder.addStretch(1)

    def _set_status(self, status):
        self.detail_status.setText("Order status updates are disabled until backend order endpoints exist.")

    def _order_by_id(self, order_id):
        return next((order for order in self.orders if order["id"] == order_id), None)

    def _update_sync_label(self):
        if hasattr(self, "sync_label"):
            timestamp = QDateTime.currentDateTime().toString("HH:mm:ss")
            self.sync_label.setText(f"Last check: {timestamp} - awaiting order API")
