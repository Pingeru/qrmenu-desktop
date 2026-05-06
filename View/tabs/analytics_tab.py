from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QPainter, QPen
from PyQt5.QtWidgets import (
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

try:
    from view.components import (
        COLORS,
        SectionHeader,
        StatCard,
        make_badge,
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

        rect = self.rect().adjusted(18, 18, -18, -28)
        axis_color = QColor("#dce3ea")
        text_color = QColor("#667585")
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
            height = int((value / max_value) * (rect.height() - 10))
            top = rect.bottom() - height
            painter.setPen(Qt.NoPen)
            painter.setBrush(self.color)
            painter.drawRoundedRect(left, top, bar_width, height, 4, 4)

            painter.setPen(QPen(text_color, 1))
            painter.drawText(left - 4, rect.bottom() + 18, bar_width + 8, 18, Qt.AlignCenter, self.labels[index])

        painter.end()


class LineChart(QWidget):
    def __init__(self, values, labels, color="#1d4ed8"):
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

        rect = self.rect().adjusted(18, 18, -18, -28)
        axis_color = QColor("#dce3ea")
        text_color = QColor("#667585")
        max_value = max(self.values) if self.values else 1
        point_count = len(self.values)
        if point_count < 2:
            painter.end()
            return

        painter.setPen(QPen(axis_color, 1))
        for index in range(5):
            y = rect.bottom() - int(rect.height() * index / 4)
            painter.drawLine(rect.left(), y, rect.right(), y)

        points = []
        for index, value in enumerate(self.values):
            x = rect.left() + int(rect.width() * index / (point_count - 1))
            y = rect.bottom() - int((value / max_value) * (rect.height() - 10))
            points.append((x, y))

        painter.setPen(QPen(self.color, 3))
        for index in range(len(points) - 1):
            painter.drawLine(points[index][0], points[index][1], points[index + 1][0], points[index + 1][1])

        painter.setBrush(QColor("#ffffff"))
        for x, y in points:
            painter.setPen(QPen(self.color, 2))
            painter.drawEllipse(x - 4, y - 4, 8, 8)

        painter.setPen(QPen(text_color, 1))
        for index, label in enumerate(self.labels):
            if index % 2 == 0 or index == len(self.labels) - 1:
                x = rect.left() + int(rect.width() * index / (point_count - 1))
                painter.drawText(x - 18, rect.bottom() + 18, 36, 18, Qt.AlignCenter, label)

        painter.end()


class Analytics_Tab(QWidget):
    def __init__(self):
        super().__init__()
        self.analytics = {
            "May 2026": {
                "orders": [18, 21, 26, 24, 34, 31, 38, 42, 37, 45, 49, 46],
                "revenue": [2860, 3310, 4140, 3890, 5480, 5120, 6375, 7020, 6210, 7590, 8160, 7810],
                "products": [
                    ("Iced Latte", 96, 8448.00),
                    ("Classic Burger", 74, 15540.00),
                    ("Fresh Lemonade", 61, 5490.00),
                    ("Chocolate Souffle", 48, 6240.00),
                    ("Caesar Salad", 39, 6045.00),
                ],
            },
            "April 2026": {
                "orders": [12, 17, 20, 18, 23, 29, 27, 31, 30, 35, 33, 39],
                "revenue": [1940, 2720, 3180, 2895, 3710, 4685, 4370, 5010, 4930, 5680, 5310, 6280],
                "products": [
                    ("Classic Burger", 68, 14280.00),
                    ("Iced Latte", 62, 5456.00),
                    ("Caesar Salad", 43, 6665.00),
                    ("Fresh Lemonade", 41, 3690.00),
                    ("Soup of the Day", 34, 2890.00),
                ],
            },
        }
        self.day_labels = ["01", "03", "05", "07", "09", "11", "13", "15", "17", "19", "21", "23"]

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(18)

        self.period_filter = QComboBox()
        self.period_filter.addItems(self.analytics.keys())
        self.period_filter.currentTextChanged.connect(self._refresh_dashboard)
        root.addWidget(
            SectionHeader(
                "Statistics Panel",
                "Track monthly revenue, top products, and daily QR order trends.",
                [make_label("Period", "muted"), self.period_filter],
            )
        )

        summary = QHBoxLayout()
        summary.setSpacing(12)
        self.revenue_card = StatCard("Current month revenue", "$ 0.00", "Completed orders", "green")
        self.order_card = StatCard("Orders", "0", "Daily volume total", "blue")
        self.average_card = StatCard("Average order", "$ 0.00", "Revenue per order", "accent")
        self.top_card = StatCard("Most ordered product", "-", "This month", "amber")
        summary.addWidget(self.revenue_card)
        summary.addWidget(self.order_card)
        summary.addWidget(self.average_card)
        summary.addWidget(self.top_card)
        root.addLayout(summary)

        dashboard = QGridLayout()
        dashboard.setSpacing(16)
        dashboard.addWidget(self._build_revenue_chart(), 0, 0)
        dashboard.addWidget(self._build_order_chart(), 0, 1)
        dashboard.addWidget(self._build_product_table(), 1, 0)
        dashboard.addWidget(self._build_insight_panel(), 1, 1)
        dashboard.setRowStretch(0, 1)
        dashboard.setRowStretch(1, 1)
        dashboard.setColumnStretch(0, 3)
        dashboard.setColumnStretch(1, 2)
        root.addLayout(dashboard, 1)

        self._refresh_dashboard()

    def _build_revenue_chart(self):
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        toolbar = QHBoxLayout()
        toolbar.addWidget(make_label("Daily Revenue", "section-title"))
        toolbar.addStretch(1)
        toolbar.addWidget(make_badge("GET /analytics/revenue", "accent"))
        layout.addLayout(toolbar)

        self.revenue_chart = LineChart([], self.day_labels, COLORS["blue"])
        layout.addWidget(self.revenue_chart, 1)
        return card

    def _build_order_chart(self):
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        toolbar = QHBoxLayout()
        toolbar.addWidget(make_label("Daily Orders", "section-title"))
        toolbar.addStretch(1)
        toolbar.addWidget(make_badge("Volume", "blue"))
        layout.addLayout(toolbar)

        self.order_chart = BarChart([], self.day_labels, COLORS["accent"])
        layout.addWidget(self.order_chart, 1)
        return card

    def _build_product_table(self):
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        toolbar = QHBoxLayout()
        toolbar.addWidget(make_label("Product Analytics", "section-title"))
        toolbar.addStretch(1)
        toolbar.addWidget(make_badge("Aggregated orders", "accent"))
        layout.addLayout(toolbar)

        self.product_table = QTableWidget(0, 4)
        self.product_table.setHorizontalHeaderLabels(["Product", "Orders", "Revenue", "Share"])
        set_table_defaults(self.product_table)
        layout.addWidget(self.product_table, 1)
        return card

    def _build_insight_panel(self):
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        layout.addWidget(make_label("Monthly Insights", "section-title"))
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

        layout.addWidget(make_label("Backend readiness", "section-title"))
        for text in [
            "Revenue Tracking: monthly income from completed orders.",
            "Product Analytics: most ordered product via aggregation.",
            "Visual Charts: daily order volume and revenue trends.",
        ]:
            row = QHBoxLayout()
            row.addWidget(make_badge("OK", "green"))
            label = make_label(text, "muted")
            label.setWordWrap(True)
            row.addWidget(label, 1)
            layout.addLayout(row)

        self.sync_status = make_label("Demo analytics are local until GET /analytics is connected.", "muted")
        self.sync_status.setWordWrap(True)
        layout.addStretch(1)
        layout.addWidget(self.sync_status)
        return card

    def _refresh_dashboard(self):
        period = self.period_filter.currentText()
        data = self.analytics[period]
        total_revenue = sum(data["revenue"])
        total_orders = sum(data["orders"])
        average_order = total_revenue / total_orders if total_orders else 0
        top_product = max(data["products"], key=lambda item: item[1])

        self.revenue_card.value_label.setText(f"$ {total_revenue:,.2f}")
        self.order_card.value_label.setText(str(total_orders))
        self.average_card.value_label.setText(f"$ {average_order:,.2f}")
        self.top_card.value_label.setText(top_product[0])
        self.revenue_chart.set_data(data["revenue"], self.day_labels)
        self.order_chart.set_data(data["orders"], self.day_labels)
        self._refresh_product_table(data["products"])
        self._refresh_insights(period, data, top_product)

    def _refresh_product_table(self, products):
        total_product_orders = sum(product[1] for product in products)
        self.product_table.setRowCount(0)
        for product_name, order_count, revenue in products:
            row = self.product_table.rowCount()
            self.product_table.insertRow(row)
            share = (order_count / total_product_orders) * 100 if total_product_orders else 0
            self.product_table.setItem(row, 0, QTableWidgetItem(product_name))
            self.product_table.setItem(row, 1, QTableWidgetItem(str(order_count)))
            self.product_table.setItem(row, 2, QTableWidgetItem(f"$ {revenue:,.2f}"))
            self.product_table.setItem(row, 3, QTableWidgetItem(f"{share:.1f}%"))

    def _refresh_insights(self, period, data, top_product):
        peak_index = data["orders"].index(max(data["orders"]))
        peak_day = self.day_labels[peak_index]
        revenue_delta = data["revenue"][-1] - data["revenue"][0]
        direction = "up" if revenue_delta >= 0 else "down"

        self.insight_title.setText(f"{top_product[0]} leads {period}")
        self.insight_body.setText(
            f"The strongest order day is {peak_day} {period.split()[0]} with "
            f"{data['orders'][peak_index]} orders. Revenue is trending {direction} "
            f"by $ {abs(revenue_delta):,.2f} across the visible period."
        )
        self.sync_status.setText(f"{period} loaded from local demo analytics. API GET /analytics can replace this data.")
