from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QFontMetrics, QPainter, QPen
from PyQt5.QtWidgets import (
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
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
        make_button,
        make_card,
        make_label,
        make_scroll_area,
        set_table_defaults,
    )
except ModuleNotFoundError:
    from components import (
        COLORS,
        SectionHeader,
        StatCard,
        make_button,
        make_card,
        make_label,
        make_scroll_area,
        set_table_defaults,
    )


def _format_money(value):
    try:
        return f"$ {float(value or 0):,.2f}"
    except (TypeError, ValueError):
        return "$ 0.00"


class HBarChart(QWidget):
    """Horizontal bar chart - keeps long category names readable."""

    def __init__(self, color="#0f766e", value_formatter=str):
        super().__init__()
        self.values = []
        self.labels = []
        self.color = QColor(color)
        self.value_formatter = value_formatter
        self.row_height = 30
        self.row_gap = 10
        self.label_width = 150
        self.value_width = 90
        self.setMinimumHeight(220)

    def set_data(self, values, labels):
        self.values = list(values or [])
        self.labels = list(labels or [])
        rows = max(1, len(self.values))
        self.setMinimumHeight(
            16 + rows * self.row_height + max(0, rows - 1) * self.row_gap + 16
        )
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        if not self.values:
            painter.setPen(QPen(QColor(COLORS["muted"])))
            painter.drawText(self.rect(), Qt.AlignCenter, "No data")
            painter.end()
            return

        max_value = max(self.values) if max(self.values) > 0 else 1
        rect = self.rect().adjusted(14, 14, -14, -14)

        text_color = QColor(COLORS["text"])
        muted = QColor(COLORS["muted"])
        track = QColor("#eef4f2")

        bar_area_left = rect.left() + self.label_width + 8
        bar_area_right = rect.right() - self.value_width - 6
        bar_area_width = max(40, bar_area_right - bar_area_left)

        font = painter.font()
        metrics = QFontMetrics(font)

        y = rect.top()
        for index, value in enumerate(self.values):
            label = self.labels[index] if index < len(self.labels) else "-"
            elided = metrics.elidedText(str(label), Qt.ElideRight, self.label_width)

            painter.setPen(QPen(text_color))
            painter.drawText(
                rect.left(), y, self.label_width, self.row_height,
                Qt.AlignVCenter | Qt.AlignLeft, elided,
            )

            painter.setPen(Qt.NoPen)
            painter.setBrush(track)
            painter.drawRoundedRect(
                bar_area_left, y + self.row_height // 2 - 7,
                bar_area_width, 14, 7, 7,
            )

            bar_w = int((value / max_value) * bar_area_width) if max_value else 0
            if bar_w > 0:
                painter.setBrush(self.color)
                painter.drawRoundedRect(
                    bar_area_left, y + self.row_height // 2 - 7,
                    max(2, bar_w), 14, 7, 7,
                )

            painter.setPen(QPen(muted))
            painter.drawText(
                bar_area_right + 4, y, self.value_width - 4, self.row_height,
                Qt.AlignVCenter | Qt.AlignRight,
                self.value_formatter(value),
            )

            y += self.row_height + self.row_gap

        painter.end()


class Analytics_Tab(QWidget):
    def __init__(self, analytics_controller=None, order_controller=None):
        super().__init__()
        self.analytics_controller = analytics_controller
        self.order_controller = order_controller

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        body = QWidget()
        root = QVBoxLayout(body)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(18)

        self.period_filter = QComboBox()
        self.period_filter.addItem("Current month")
        self.period_filter.setEnabled(False)
        self.period_filter.setMinimumWidth(160)
        refresh_button = make_button("Refresh", "primary")
        refresh_button.clicked.connect(lambda: self._load_analytics(show_error=True))
        root.addWidget(
            SectionHeader(
                "Statistics Panel",
                "Performance summary from qrmenu-api business analytics.",
                [make_label("Period", "muted"), self.period_filter, refresh_button],
            )
        )

        # KPI cards
        summary = QHBoxLayout()
        summary.setSpacing(12)
        self.revenue_card = StatCard("Revenue", "$ 0.00", "Selected period", "green")
        self.order_card = StatCard("Orders", "0", "Total orders", "blue")
        self.average_card = StatCard("Average order", "$ 0.00", "Revenue per order", "accent")
        self.top_card = StatCard("Top product", "-", "By quantity sold", "amber")
        summary.addWidget(self.revenue_card)
        summary.addWidget(self.order_card)
        summary.addWidget(self.average_card)
        summary.addWidget(self.top_card)
        root.addLayout(summary)

        # Main content with empty-state overlay
        self.content_stack = QStackedLayout()
        self.content_stack.setContentsMargins(0, 0, 0, 0)
        stack_holder = QWidget()
        stack_holder.setLayout(self.content_stack)

        self.dashboard_widget = self._build_dashboard()
        self.empty_state_widget = self._build_empty_state()
        self.content_stack.addWidget(self.dashboard_widget)
        self.content_stack.addWidget(self.empty_state_widget)
        root.addWidget(stack_holder, 1)

        outer.addWidget(make_scroll_area(body), 1)

        self._load_analytics(show_error=False)

    # ---------- Builders ----------

    def _build_dashboard(self):
        wrapper = QWidget()
        grid = QGridLayout(wrapper)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(16)
        grid.addWidget(self._build_revenue_chart(), 0, 0)
        grid.addWidget(self._build_quantity_chart(), 0, 1)
        grid.addWidget(self._build_product_table(), 1, 0)
        grid.addWidget(self._build_insight_panel(), 1, 1)
        grid.setColumnStretch(0, 3)
        grid.setColumnStretch(1, 2)
        grid.setRowMinimumHeight(0, 280)
        grid.setRowMinimumHeight(1, 280)
        return wrapper

    def _build_revenue_chart(self):
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        layout.addWidget(make_label("Category Revenue", "section-title"))
        layout.addWidget(
            make_label("Revenue per category for the selected period.", "muted")
        )
        self.revenue_chart = HBarChart(COLORS["accent"], _format_money)
        layout.addWidget(self.revenue_chart, 1)
        return card

    def _build_quantity_chart(self):
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        layout.addWidget(make_label("Category Items", "section-title"))
        layout.addWidget(
            make_label("Items sold per category for the selected period.", "muted")
        )
        self.quantity_chart = HBarChart(COLORS["blue"], lambda v: str(int(v)))
        layout.addWidget(self.quantity_chart, 1)
        return card

    def _build_product_table(self):
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        layout.addWidget(make_label("Product Analytics", "section-title"))
        layout.addWidget(
            make_label("Top products by quantity sold.", "muted")
        )

        self.product_table = QTableWidget(0, 4)
        self.product_table.setHorizontalHeaderLabels(["Product", "Items", "Revenue", "Share"])
        set_table_defaults(self.product_table)
        header = self.product_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        layout.addWidget(self.product_table, 1)
        return card

    def _build_insight_panel(self):
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        layout.addWidget(make_label("Insights", "section-title"))

        self.insight_title = QLabel("-")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        self.insight_title.setFont(title_font)
        self.insight_title.setStyleSheet(f"color: {COLORS['accent']};")
        self.insight_title.setWordWrap(True)
        layout.addWidget(self.insight_title)

        self.insight_body = make_label("", "subtitle")
        self.insight_body.setWordWrap(True)
        layout.addWidget(self.insight_body)

        layout.addStretch(1)

        self.sync_status = make_label("", "muted")
        self.sync_status.setWordWrap(True)
        layout.addWidget(self.sync_status)
        return card

    def _build_empty_state(self):
        card = make_card()
        v = QVBoxLayout(card)
        v.setContentsMargins(20, 60, 20, 60)
        v.addStretch(1)

        title = make_label("No analytics data for this period yet.")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {COLORS['text']};")
        v.addWidget(title)

        subtitle = make_label(
            "Analytics will appear once your menu starts receiving customer orders.",
            "muted",
        )
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        v.addWidget(subtitle)

        self.empty_reason = make_label("", "muted")
        self.empty_reason.setAlignment(Qt.AlignCenter)
        self.empty_reason.setWordWrap(True)
        v.addWidget(self.empty_reason)
        v.addStretch(1)
        return card

    # ---------- Data ----------

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

        self._refresh_from_payload(payload or {})

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

        orders = orders or []
        total_revenue = sum(self._to_float(order.get("total_amount")) for order in orders)
        total_orders = len(orders)
        payload = {
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "average_order_value": (total_revenue / total_orders) if total_orders else 0,
            "total_items": sum(
                int(item.get("quantity") or 0)
                for order in orders
                for item in (order.get("items") or [])
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

        self.revenue_card.value_label.setText(_format_money(total_revenue))
        self.order_card.value_label.setText(str(total_orders))
        self.average_card.value_label.setText(_format_money(average_order))
        self.top_card.value_label.setText(top_product_name)

        # If backend returns nothing meaningful, show empty state instead of empty charts.
        if total_orders == 0 and not top_products and not top_categories:
            self._show_empty_state(
                fallback_reason
                or "No analytics data for this period yet."
            )
            return

        self.content_stack.setCurrentWidget(self.dashboard_widget)

        chart_source = top_categories or self._categories_from_products(top_products)
        chart_source = chart_source[:8]

        self.revenue_chart.set_data(
            [self._entry_revenue(item) for item in chart_source],
            [self._entry_name(item) for item in chart_source],
        )
        self.quantity_chart.set_data(
            [self._entry_quantity(item) for item in chart_source],
            [self._entry_name(item) for item in chart_source],
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
        self.empty_reason.setText(message or "")
        self.content_stack.setCurrentWidget(self.empty_state_widget)

    def _refresh_product_table(self, products):
        total_items = sum(self._entry_quantity(product) for product in products)
        self.product_table.setRowCount(0)
        for product in products:
            row = self.product_table.rowCount()
            self.product_table.insertRow(row)
            quantity = self._entry_quantity(product)
            share = (quantity / total_items) * 100 if total_items else 0

            name_item = QTableWidgetItem(self._product_name(product))
            qty_item = QTableWidgetItem(str(quantity))
            qty_item.setTextAlignment(Qt.AlignCenter)
            rev_item = QTableWidgetItem(_format_money(self._entry_revenue(product)))
            rev_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            share_item = QTableWidgetItem(f"{share:.1f} %")
            share_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            self.product_table.setItem(row, 0, name_item)
            self.product_table.setItem(row, 1, qty_item)
            self.product_table.setItem(row, 2, rev_item)
            self.product_table.setItem(row, 3, share_item)

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
        top_product = self._product_name(top_products[0]) if top_products else None
        if top_product:
            self.insight_title.setText(f"{top_product} leads the period")
        else:
            self.insight_title.setText("Period summary")

        lines = [
            f"{total_orders} orders generated {_format_money(total_revenue)} "
            f"across {total_items} items sold."
        ]
        if top_categories:
            lines.append(f"Top category: {self._entry_name(top_categories[0])}.")
        if least_sold_products:
            lines.append(
                f"Least sold product: {self._product_name(least_sold_products[0])}."
            )
        if least_sold_category:
            lines.append(
                f"Least sold category: {self._entry_name(least_sold_category)}."
            )
        self.insight_body.setText("\n".join(lines))

        if fallback_reason:
            self.sync_status.setText(
                f"Showing order-derived metrics (analytics endpoint: {fallback_reason})."
            )
        else:
            self.sync_status.setText("Data source: /business/analytics")

    # ---------- Helpers ----------

    def _product_entries_from_orders(self, orders):
        products = {}
        for order in orders:
            for item in (order.get("items") or []):
                product_id = str(item.get("product_id") or "unknown")
                product_name = (item.get("product_name") or "").strip()
                if not product_name:
                    product_name = (
                        f"Product {product_id[-6:]}"
                        if product_id != "unknown"
                        else "Unknown product"
                    )
                quantity = int(item.get("quantity") or 0)
                revenue = self._to_float(item.get("price_at_purchase")) * quantity
                current = products.setdefault(
                    product_name, {"sold_quantity": 0, "sold_revenue": 0.0}
                )
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
