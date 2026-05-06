from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QCursor, QFont, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import (
    QFrame,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)


COLORS = {
    "bg": "#f5f7fa",
    "surface": "#ffffff",
    "surface_alt": "#f9fbfc",
    "border": "#dce3ea",
    "text": "#14212b",
    "muted": "#667585",
    "accent": "#0f766e",
    "accent_dark": "#0b5f59",
    "amber": "#b7791f",
    "green": "#15803d",
    "red": "#b42318",
    "blue": "#1d4ed8",
}


def app_stylesheet():
    return """
    * {
        font-family: "Segoe UI", Arial, sans-serif;
        color: #14212b;
        font-size: 13px;
    }

    QWidget#LoginPage,
    QWidget#HomePage {
        background: #f5f7fa;
    }

    QFrame#Card {
        background: #ffffff;
        border: 1px solid #dce3ea;
        border-radius: 8px;
    }

    QLabel[role="title"] {
        color: #111827;
        font-size: 22px;
        font-weight: 700;
    }

    QLabel[role="subtitle"] {
        color: #667585;
        font-size: 13px;
    }

    QLabel[role="section-title"] {
        color: #14212b;
        font-size: 16px;
        font-weight: 700;
    }

    QLabel[role="muted"] {
        color: #667585;
    }

    QLineEdit,
    QTextEdit,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox {
        background: #ffffff;
        border: 1px solid #cfd8e3;
        border-radius: 6px;
        padding: 8px 10px;
        selection-background-color: #0f766e;
        min-height: 22px;
    }

    QTextEdit {
        padding: 8px;
    }

    QLineEdit:focus,
    QTextEdit:focus,
    QComboBox:focus,
    QSpinBox:focus,
    QDoubleSpinBox:focus {
        border: 1px solid #0f766e;
    }

    QPushButton {
        border: 1px solid #cfd8e3;
        border-radius: 6px;
        padding: 8px 14px;
        background: #ffffff;
        color: #14212b;
        font-weight: 600;
    }

    QPushButton:hover {
        background: #f2f6f8;
    }

    QPushButton[variant="primary"] {
        background: #0f766e;
        border-color: #0f766e;
        color: #ffffff;
    }

    QPushButton[variant="primary"]:hover {
        background: #0b5f59;
        border-color: #0b5f59;
    }

    QPushButton[variant="danger"] {
        color: #b42318;
        border-color: #f1b7b1;
        background: #fff7f6;
    }

    QPushButton[variant="ghost"] {
        background: transparent;
        border-color: transparent;
        color: #0f766e;
        padding-left: 8px;
        padding-right: 8px;
    }

    QTabWidget::pane {
        border: 1px solid #dce3ea;
        background: #ffffff;
        border-radius: 8px;
        top: -1px;
    }

    QTabBar::tab {
        background: #edf2f5;
        color: #526170;
        border: 1px solid #dce3ea;
        border-bottom: none;
        border-top-left-radius: 7px;
        border-top-right-radius: 7px;
        padding: 10px 18px;
        margin-right: 4px;
        font-weight: 600;
    }

    QTabBar::tab:selected {
        background: #ffffff;
        color: #0f766e;
    }

    QListWidget {
        background: #ffffff;
        border: 1px solid #dce3ea;
        border-radius: 8px;
        padding: 6px;
    }

    QListWidget::item {
        padding: 9px 10px;
        border-radius: 6px;
    }

    QListWidget::item:selected {
        background: #e4f3f0;
        color: #0f766e;
        font-weight: 700;
    }

    QTableWidget {
        background: #ffffff;
        border: 1px solid #dce3ea;
        border-radius: 8px;
        gridline-color: #edf1f4;
        selection-background-color: #e4f3f0;
        selection-color: #14212b;
        alternate-background-color: #f9fbfc;
    }

    QHeaderView::section {
        background: #f3f6f8;
        color: #526170;
        border: none;
        border-bottom: 1px solid #dce3ea;
        padding: 9px 10px;
        font-weight: 700;
    }

    QScrollBar:vertical {
        background: #f5f7fa;
        width: 10px;
        margin: 2px;
    }

    QScrollBar::handle:vertical {
        background: #c7d2de;
        border-radius: 5px;
        min-height: 32px;
    }
    """


def make_card(object_name="Card"):
    card = QFrame()
    card.setObjectName(object_name)
    return card


def make_button(text, variant="default"):
    button = QPushButton(text)
    button.setCursor(QCursor(Qt.PointingHandCursor))
    button.setProperty("variant", variant)
    return button


def make_label(text, role=None):
    label = QLabel(text)
    if role:
        label.setProperty("role", role)
    return label


def make_badge(text, tone="neutral"):
    colors = {
        "neutral": ("#eef2f6", "#526170"),
        "accent": ("#e4f3f0", "#0f766e"),
        "amber": ("#fff4df", "#996515"),
        "green": ("#e8f5ec", "#15803d"),
        "red": ("#fff0ee", "#b42318"),
        "blue": ("#eaf1ff", "#1d4ed8"),
    }
    background, color = colors.get(tone, colors["neutral"])
    label = QLabel(text)
    label.setAlignment(Qt.AlignCenter)
    label.setStyleSheet(
        f"background: {background}; color: {color}; border-radius: 10px; "
        "padding: 3px 9px; font-weight: 700;"
    )
    return label


class StatCard(QFrame):
    def __init__(self, title, value, detail="", tone="accent"):
        super().__init__()
        self.setObjectName("Card")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        title_label = make_label(title, "muted")
        self.value_label = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(21)
        value_font.setBold(True)
        self.value_label.setFont(value_font)
        self.value_label.setStyleSheet(f"color: {COLORS.get(tone, COLORS['accent'])};")
        detail_label = make_label(detail, "muted")

        layout.addWidget(title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(detail_label)


class SectionHeader(QWidget):
    def __init__(self, title, subtitle="", actions=None):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        text_group = QVBoxLayout()
        text_group.setSpacing(3)
        text_group.addWidget(make_label(title, "section-title"))
        if subtitle:
            text_group.addWidget(make_label(subtitle, "subtitle"))

        layout.addLayout(text_group, 1)

        if actions:
            for action in actions:
                layout.addWidget(action)


def set_table_defaults(table):
    table.setAlternatingRowColors(True)
    table.setShowGrid(False)
    table.verticalHeader().setVisible(False)
    table.verticalHeader().setDefaultSectionSize(44)
    table.horizontalHeader().setStretchLastSection(True)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    table.setSelectionBehavior(QTableWidget.SelectRows)
    table.setSelectionMode(QTableWidget.SingleSelection)


def build_qr_pixmap(seed_text, size=180):
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor("#ffffff"))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing, False)
    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor("#14212b"))

    cell_count = 25
    margin = 12
    cell = (size - (margin * 2)) // cell_count

    def draw_finder(x, y):
        painter.setBrush(QColor("#14212b"))
        painter.drawRect(margin + x * cell, margin + y * cell, cell * 7, cell * 7)
        painter.setBrush(QColor("#ffffff"))
        painter.drawRect(margin + (x + 1) * cell, margin + (y + 1) * cell, cell * 5, cell * 5)
        painter.setBrush(QColor("#14212b"))
        painter.drawRect(margin + (x + 2) * cell, margin + (y + 2) * cell, cell * 3, cell * 3)

    draw_finder(0, 0)
    draw_finder(18, 0)
    draw_finder(0, 18)

    seed = sum(ord(char) for char in seed_text)
    painter.setBrush(QColor("#14212b"))
    for row in range(cell_count):
        for col in range(cell_count):
            in_finder = (
                (row < 8 and col < 8)
                or (row < 8 and col > 16)
                or (row > 16 and col < 8)
            )
            if in_finder:
                continue
            bit = (row * 17 + col * 31 + seed) % 7
            if bit in (0, 2, 5):
                painter.drawRect(margin + col * cell, margin + row * cell, cell, cell)

    painter.setPen(QPen(QColor("#dce3ea"), 1))
    painter.setBrush(Qt.NoBrush)
    painter.drawRect(0, 0, size - 1, size - 1)
    painter.end()
    return pixmap
