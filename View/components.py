from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QCursor, QFont, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import (
    QFrame,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)


COLORS = {
    "bg": "#eef3f1",
    "surface": "#ffffff",
    "surface_alt": "#f7faf9",
    "border": "#d8e2df",
    "text": "#17211d",
    "muted": "#65736f",
    "accent": "#0f766e",
    "accent_dark": "#0b5f59",
    "amber": "#b7791f",
    "green": "#15803d",
    "red": "#b42318",
    "blue": "#2563eb",
    "coral": "#c2410c",
    "ink": "#10231f",
}


def app_stylesheet():
    return """
    * {
        font-family: "Segoe UI", Arial, sans-serif;
        color: #17211d;
        font-size: 13px;
    }

    QWidget#LoginPage,
    QWidget#HomePage {
        background: #eef3f1;
    }

    QFrame#Card {
        background: #ffffff;
        border: 1px solid #d8e2df;
        border-radius: 8px;
    }

    QFrame#AuthCard {
        background: #ffffff;
        border: 1px solid #d8e2df;
        border-radius: 8px;
    }

    QLabel#AuthMark {
        background: #10231f;
        color: #e7fff8;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 800;
    }

    QLabel#AuthTitle {
        color: #17211d;
        font-size: 23px;
        font-weight: 800;
    }

    QLabel#AuthSubtitle {
        color: #65736f;
        font-size: 13px;
    }

    QFrame#AuthCard QLineEdit {
        min-width: 310px;
    }

    QFrame#AppHeader {
        background: #10231f;
        border: 1px solid #18342e;
        border-radius: 8px;
    }

    QLabel#BrandMark {
        background: #e7fff8;
        color: #0b5f59;
        border-radius: 16px;
        font-size: 13px;
        font-weight: 800;
    }

    QLabel#HeaderTitle {
        color: #ffffff;
        font-size: 20px;
        font-weight: 800;
    }

    QLabel#HeaderSubtitle {
        color: #a7bbb5;
        font-size: 12px;
    }

    QFrame#AppHeader QPushButton[variant="ghost"] {
        color: #e7fff8;
        border-color: transparent;
    }

    QFrame#AppHeader QPushButton[variant="ghost"]:hover {
        background: #18342e;
    }

    QLabel[role="title"] {
        color: #17211d;
        font-size: 22px;
        font-weight: 800;
    }

    QLabel[role="subtitle"] {
        color: #65736f;
        font-size: 13px;
    }

    QLabel[role="section-title"] {
        color: #17211d;
        font-size: 16px;
        font-weight: 800;
    }

    QLabel[role="muted"] {
        color: #65736f;
    }

    QWidget#SectionHeader {
        background: transparent;
    }

    QLineEdit,
    QTextEdit,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox {
        background: #ffffff;
        border: 1px solid #cbd8d4;
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
        background: #fbfefd;
    }

    QPushButton {
        border: 1px solid #cbd8d4;
        border-radius: 6px;
        padding: 8px 14px;
        background: #ffffff;
        color: #17211d;
        font-weight: 700;
        min-height: 20px;
    }

    QPushButton:hover {
        background: #f3f8f6;
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
        border-color: #efc0ba;
        background: #fff8f7;
    }

    QPushButton[variant="ghost"] {
        background: transparent;
        border-color: transparent;
        color: #0f766e;
    }

    QPushButton:disabled {
        color: #9aa8a4;
        border-color: #dde6e3;
        background: #f4f7f6;
    }

    QTabWidget::pane {
        border: 1px solid #d8e2df;
        background: #ffffff;
        border-radius: 8px;
        top: -1px;
    }

    QTabBar::tab {
        background: #e5ece9;
        color: #586964;
        border: 1px solid #d8e2df;
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
        border-top: 2px solid #0f766e;
    }

    QTabBar::tab:hover:!selected {
        background: #f1f6f4;
        color: #17211d;
    }

    QListWidget {
        background: #ffffff;
        border: 1px solid #d8e2df;
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
        border: 1px solid #d8e2df;
        border-radius: 8px;
        gridline-color: #eef3f1;
        selection-background-color: #e4f3f0;
        selection-color: #17211d;
        alternate-background-color: #f7faf9;
    }

    QHeaderView::section {
        background: #eef4f2;
        color: #586964;
        border: none;
        border-bottom: 1px solid #d8e2df;
        padding: 9px 10px;
        font-weight: 700;
    }

    QScrollBar:vertical {
        background: #eef3f1;
        width: 10px;
        margin: 2px;
    }

    QScrollBar::handle:vertical {
        background: #bdcbc7;
        border-radius: 5px;
        min-height: 32px;
    }

    QScrollArea {
        border: none;
        background: transparent;
    }
    """


def make_card(object_name="Card"):
    card = QFrame()
    card.setObjectName(object_name)
    return card


def make_scroll_area(widget):
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setFrameShape(QFrame.NoFrame)
    scroll_area.setWidget(widget)
    return scroll_area


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
        "neutral": ("#eef4f2", "#586964"),
        "accent": ("#e4f3f0", "#0f766e"),
        "amber": ("#fff4df", "#996515"),
        "green": ("#e8f5ec", "#15803d"),
        "red": ("#fff0ee", "#b42318"),
        "blue": ("#eaf1ff", "#2563eb"),
        "coral": ("#fff1e8", "#c2410c"),
        "dark": ("#18342e", "#e7fff8"),
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
        layout.setContentsMargins(16, 12, 16, 14)
        layout.setSpacing(7)

        accent_bar = QFrame()
        accent_bar.setFixedHeight(3)
        accent_bar.setStyleSheet(
            f"background: {COLORS.get(tone, COLORS['accent'])}; border-radius: 1px;"
        )
        layout.addWidget(accent_bar)

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
        self.setObjectName("SectionHeader")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        text_group = QVBoxLayout()
        text_group.setSpacing(4)
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
