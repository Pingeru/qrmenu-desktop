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
        self.analytics = {}
        self.day_labels = []

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(18)

        self.period_filter = QComboBox()
        self.period_filter.addItem("No backend data")
        self.period_filter.setEnabled(False)
        self.period_filter.currentTextChanged.connect(self._refresh_dashboard)
        root.addWidget(
            SectionHeader(
                "Statistics Panel",
                "Analytics endpoints are not available yet; this view will stay empty until backend data exists.",
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
        toolbar.addWidget(make_badge("Awaiting API", "neutral"))
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
        toolbar.addWidget(make_badge("Awaiting API", "neutral"))
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
        toolbar.addWidget(make_badge("Awaiting API", "neutral"))
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
            row.addWidget(make_badge("Pending", "amber"))
            label = make_label(text, "muted")
            label.setWordWrap(True)
            row.addWidget(label, 1)
            layout.addLayout(row)

        self.sync_status = make_label("No analytics data is loaded because the backend does not expose analytics endpoints yet.", "muted")
        self.sync_status.setWordWrap(True)
        layout.addStretch(1)
        layout.addWidget(self.sync_status)
        return card

    def _refresh_dashboard(self):
        self.revenue_card.value_label.setText("$ 0.00")
        self.order_card.value_label.setText("0")
        self.average_card.value_label.setText("$ 0.00")
        self.top_card.value_label.setText("-")
        self.revenue_chart.set_data([], [])
        self.order_chart.set_data([], [])
        self._refresh_product_table([])
        self.insight_title.setText("Analytics endpoint pending")
        self.insight_body.setText("Backend analytics routes are not available yet, so no demo revenue, order, or product ranking data is displayed.")
        self.sync_status.setText("Waiting for backend analytics endpoints.")

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
        if not data["orders"]:
            self.insight_title.setText("Analytics endpoint pending")
            self.insight_body.setText("No analytics data is available yet.")
            return
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
