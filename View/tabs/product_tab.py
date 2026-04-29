
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QFont


class Product_Tab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("Ürünler içeriği buraya gelecek.")
        label_font = QFont()
        label_font.setPointSize(12)
        label.setFont(label_font)
        layout.addWidget(label)