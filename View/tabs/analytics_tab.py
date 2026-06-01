from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QPainter, QPen
from PyQt5.QtWidgets import (
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
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


class BarChart(QWidget):
    def __init__(self, values, labels, color="#0f766e"):
        super().__init__()
        self.values = values
        self.labels = labels
        self.color = QColor(color)
        self.setMinimumHeight(220)

    def set_data(self, values, labels):
        self.values = values
        self.labels = labels
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(18, 18, -18, -34)
        axis_color = QColor("#d8e2df")
        text_color = QColor("#65736f")
        max_value = max(self.values) if self.values else 1
        bar_count = len(self.values)
        if not bar_count:
            painter.end()
            return

        painter.setPen(QPen(axis_color, 1))
        for index in range(5):
            y = rect.bottom() - int(rect.height() * index / 4)
            painter.drawLine(rect.left(), y, rect.right(), y)

        gap = 10
        bar_width = max(16, int((rect.width() - gap * (bar_count - 1)) / bar_count))
        for index, value in enumerate(self.values):
            left = rect.left() + index * (bar_width + gap)
            height = int((value / max_value) * (rect.height() - 10)) if max_value else 0
            top = rect.bottom() - height
            painter.setPen(Qt.NoPen)
            painter.setBrush(self.color)
            painter.drawRoundedRect(left, top, bar_width, height, 4, 4)

            label = self.labels[index]
            if len(label) > 10:
                label = f"{label[:9]}."
            painter.setPen(QPen(text_color, 1))
            painter.drawText(left - 8, rect.bottom() + 18, bar_width + 16, 18, Qt.AlignCenter, label)

        painter.end()


class Analytics_Tab(QWidget):
    def __init__(self, analytics_controller=None, order_controller=None):
        super().__init__()
        self.analytics_controller = analytics_controller
        self.order_controller = order_controller

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(18)

        self.period_filter = QComboBox()
        self.period_filter.addItem("Current month")
        self.period_filter.setEnabled(False)
        refresh_button = make_button("Refresh")
        refresh_button.clicked.connect(lambda: self._load_analytics(show_error=True))
        root.addWidget(
            SectionHeader(
                "Statistics Panel",
                "Revenue, order volume, and product rankings from GET /business/analytics.",
                [make_label("Period", "muted"), self.period_filter, refresh_button],
            )
        )

        summary = QHBoxLayout()
        summary.setSpacing(12)
        self.revenue_card = StatCard("Revenue", "$ 0.00", "Selected period", "green")
        self.order_card = StatCard("Orders", "0", "Total orders", "blue")
        self.average_card = StatCard("Average order", "$ 0.00", "Revenue per order", "accent")
        self.top_card = StatCard("Top product", "-", "By quantity", "amber")
        summary.addWidget(self.revenue_card)
        summary.addWidget(self.order_card)
        summary.addWidget(self.average_card)
        summary.addWidget(self.top_card)
        root.addLayout(summary)

        dashboard = QGridLayout()
        dashboard.setSpacing(16)
        dashboard.addWidget(self._build_revenue_chart(), 0, 0)
        dashboard.addWidget(self._build_quantity_chart(), 0, 1)
        dashboard.addWidget(self._build_product_table(), 1, 0)
        dashboard.addWidget(self._build_insight_panel(), 1, 1)
        dashboard.setRowStretch(0, 1)
        dashboard.setRowStretch(1, 1)
        dashboard.setColumnStretch(0, 3)
        dashboard.setColumnStretch(1, 2)
        root.addLayout(dashboard, 1)

        self._load_analytics(show_error=False)

    def _build_revenue_chart(self):
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        toolbar = QHBoxLayout()
        toolbar.addWidget(make_label("Category Revenue", "section-title"))
        toolbar.addStretch(1)
        toolbar.addWidget(make_badge("Analytics API", "accent"))
        layout.addLayout(toolbar)

        self.revenue_chart = BarChart([], [], COLORS["blue"])
        layout.addWidget(self.revenue_chart, 1)
        return card

    def _build_quantity_chart(self):
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        toolbar = QHBoxLayout()
        toolbar.addWidget(make_label("Category Items", "section-title"))
        toolbar.addStretch(1)
        toolbar.addWidget(make_badge("Analytics API", "accent"))
        layout.addLayout(toolbar)

        self.quantity_chart = BarChart([], [], COLORS["accent"])
        layout.addWidget(self.quantity_chart, 1)
        return card

    def _build_product_table(self):
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        toolbar = QHBoxLayout()
        toolbar.addWidget(make_label("Product Analytics", "section-title"))
        toolbar.addStretch(1)
        toolbar.addWidget(make_badge("Top products", "accent"))
        layout.addLayout(toolbar)

        self.product_table = QTableWidget(0, 4)
        self.product_table.setHorizontalHeaderLabels(["Product", "Items", "Revenue", "Share"])
        set_table_defaults(self.product_table)
        layout.addWidget(self.product_table, 1)
        return card

    def _build_insight_panel(self):
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        layout.addWidget(make_label("Insights", "section-title"))
        self.insight_title = QLabel("-")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        self.insight_title.setFont(title_font)
        self.insight_title.setStyleSheet(f"color: {COLORS['accent']};")
        layout.addWidget(self.insight_title)

        self.insight_body = make_label("", "subtitle")
        self.insight_body.setWordWrap(True)
        layout.addWidget(self.insight_body)

        layout.addWidget(make_label("Backend coverage", "section-title"))
        for text in [
            "Totals: orders, revenue, average order, total sold items.",
            "Rankings: top and least sold products.",
            "Categories: top and least sold category performance.",
        ]:
            row = QHBoxLayout()
            row.addWidget(make_badge("Live", "green"))
            label = make_label(text, "muted")
            label.setWordWrap(True)
            row.addWidget(label, 1)
            layout.addLayout(row)

        self.sync_status = make_label("Waiting for business analytics data from qrmenu-api.", "muted")
        self.sync_status.setWordWrap(True)
        layout.addStretch(1)
        layout.addWidget(self.sync_status)
        return card

    def _load_analytics(self, show_error=False):
        if not self.analytics_controller:
            self._load_order_fallback(show_error)
            return

        try:
            payload = self.analytics_controller.load_summary()
        except ApiError as exc:
            if show_error:
                QMessageBox.warning(self, "Analytics sync failed", str(exc))
            self._load_order_fallback(show_error=False, reason=str(exc))
            return

        self._refresh_from_payload(payload)

    def _load_order_fallback(self, show_error=False, reason="Analytics endpoint is not connected."):
        if not self.order_controller:
            self._show_empty_state(reason)
            return

        try:
            orders = self.order_controller.load_orders()
        except ApiError as exc:
            self._show_empty_state(f"Analytics fallback failed: {exc}")
            if show_error:
                QMessageBox.warning(self, "Analytics fallback failed", str(exc))
            return

        total_revenue = sum(self._to_float(order.get("total_amount")) for order in orders)
        total_orders = len(orders)
        payload = {
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "average_order_value": total_revenue / total_orders if total_orders else 0,
            "total_items": sum(
                int(item.get("quantity") or 0)
                for order in orders
                for item in order.get("items", [])
            ),
            "top_products": self._product_entries_from_orders(orders),
            "least_sold_products": [],
            "top_categories": [],
            "least_sold_category": None,
        }
        self._refresh_from_payload(payload, fallback_reason=reason)

    def _refresh_from_payload(self, payload, fallback_reason=None):
        top_products = payload.get("top_products") or []
        least_sold_products = payload.get("least_sold_products") or []
        top_categories = payload.get("top_categories") or []
        least_sold_category = payload.get("least_sold_category")

        total_orders = int(payload.get("total_orders") or 0)
        total_revenue = self._to_float(payload.get("total_revenue"))
        average_order = self._to_float(payload.get("average_order_value"))
        total_items = int(payload.get("total_items") or 0)
        top_product_name = self._product_name(top_products[0]) if top_products else "-"

        self.revenue_card.value_label.setText(f"$ {total_revenue:,.2f}")
        self.order_card.value_label.setText(str(total_orders))
        self.average_card.value_label.setText(f"$ {average_order:,.2f}")
        self.top_card.value_label.setText(top_product_name)

        chart_source = top_categories or self._categories_from_products(top_products)
        self.revenue_chart.set_data(
            [self._entry_revenue(item) for item in chart_source[:8]],
            [self._entry_name(item) for item in chart_source[:8]],
        )
        self.quantity_chart.set_data(
            [self._entry_quantity(item) for item in chart_source[:8]],
            [self._entry_name(item) for item in chart_source[:8]],
        )
        self._refresh_product_table(top_products)
        self._refresh_insights(
            total_orders=total_orders,
            total_revenue=total_revenue,
            total_items=total_items,
            top_products=top_products,
            least_sold_products=least_sold_products,
            top_categories=top_categories,
            least_sold_category=least_sold_category,
            fallback_reason=fallback_reason,
        )

    def _show_empty_state(self, message):
        self.revenue_card.value_label.setText("$ 0.00")
        self.order_card.value_label.setText("0")
        self.average_card.value_label.setText("$ 0.00")
        self.top_card.value_label.setText("-")
        self.revenue_chart.set_data([], [])
        self.quantity_chart.set_data([], [])
        self._refresh_product_table([])
        self.insight_title.setText("No analytics")
        self.insight_body.setText(message)
        self.sync_status.setText(message)

    def _refresh_product_table(self, products):
        total_items = sum(self._entry_quantity(product) for product in products)
        self.product_table.setRowCount(0)
        for product in products:
            row = self.product_table.rowCount()
            self.product_table.insertRow(row)
            quantity = self._entry_quantity(product)
            share = (quantity / total_items) * 100 if total_items else 0
            self.product_table.setItem(row, 0, QTableWidgetItem(self._product_name(product)))
            self.product_table.setItem(row, 1, QTableWidgetItem(str(quantity)))
            self.product_table.setItem(row, 2, QTableWidgetItem(f"$ {self._entry_revenue(product):,.2f}"))
            self.product_table.setItem(row, 3, QTableWidgetItem(f"{share:.1f}%"))

    def _refresh_insights(
        self,
        *,
        total_orders,
        total_revenue,
        total_items,
        top_products,
        least_sold_products,
        top_categories,
        least_sold_category,
        fallback_reason,
    ):
        if total_orders == 0:
            self.insight_title.setText("No orders yet")
            self.insight_body.setText("Analytics endpoint returned no orders for the selected period.")
        else:
            top_product = self._product_name(top_products[0]) if top_products else "No product detail"
            top_category = self._entry_name(top_categories[0]) if top_categories else "-"
            least_product = self._product_name(least_sold_products[0]) if least_sold_products else "-"
            least_category = self._entry_name(least_sold_category) if least_sold_category else "-"
            self.insight_title.setText(f"{top_product} leads")
            self.insight_body.setText(
                f"{total_orders} orders produced $ {total_revenue:,.2f} and {total_items} sold items. "
                f"Top category: {top_category}. Least sold product: {least_product}. "
                f"Least sold category: {least_category}."
            )

        if fallback_reason:
            self.sync_status.setText(f"Using order fallback because analytics failed: {fallback_reason}")
        else:
            self.sync_status.setText("Loaded from GET /business/analytics.")

    def _product_entries_from_orders(self, orders):
        products = {}
        for order in orders:
            for item in order.get("items", []):
                product_id = str(item.get("product_id") or "unknown")
                product_name = (item.get("product_name") or "").strip()
                if not product_name:
                    product_name = f"Product {product_id[-6:]}" if product_id != "unknown" else "Unknown product"
                quantity = int(item.get("quantity") or 0)
                revenue = self._to_float(item.get("price_at_purchase")) * quantity
                current = products.setdefault(product_name, {"sold_quantity": 0, "sold_revenue": 0.0})
                current["sold_quantity"] += quantity
                current["sold_revenue"] += revenue
        return [
            {"product": {"name": name}, **values}
            for name, values in sorted(
                products.items(),
                key=lambda item: (item[1]["sold_quantity"], item[1]["sold_revenue"]),
                reverse=True,
            )
        ]

    def _categories_from_products(self, products):
        return [
            {
                "category": {"name": self._product_name(product)},
                "sold_quantity": self._entry_quantity(product),
                "sold_revenue": self._entry_revenue(product),
            }
            for product in products
        ]

    def _entry_name(self, entry):
        if not isinstance(entry, dict):
            return "-"
        source = entry.get("category") or entry.get("product") or entry
        if isinstance(source, dict):
            return source.get("name") or "-"
        return "-"

    def _product_name(self, entry):
        if not isinstance(entry, dict):
            return "-"
        product = entry.get("product") or {}
        return product.get("name") or "-"

    def _entry_quantity(self, entry):
        if not isinstance(entry, dict):
            return 0
        return int(entry.get("sold_quantity") or 0)

    def _entry_revenue(self, entry):
        if not isinstance(entry, dict):
            return 0.0
        return self._to_float(entry.get("sold_revenue"))

    def _to_float(self, value):
        try:
            return float(value or 0)
        except (TypeError, ValueError):
            return 0.0
