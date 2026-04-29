from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QLabel,
    QTabWidget,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from tabs.category_tab import Catagory_Tab
from tabs.order_tab import Order_Tab
from tabs.product_tab import Product_Tab
from tabs.profile_tab import Profile_Tab


class Main_Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project X")
        self.setGeometry(50, 50, 1300, 900)

        self._username = "admin"
        self._password = "1"

        self.stack = QStackedWidget()
        self.login_page = self._create_login_page()
        self.home_page = self._create_home_page()

        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.home_page)
        self.setCentralWidget(self.stack)

    def _create_login_page(self):
        page = QWidget()
        outer_layout = QVBoxLayout(page)
        outer_layout.setAlignment(Qt.AlignCenter)

        card = QWidget()
        card.setMaximumWidth(360)
        form_layout = QGridLayout(card)

        title = QLabel("Giriş Yap")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title.setFont(title_font)

        username_label = QLabel("Kullanıcı Adı")
        label_font = QFont()
        label_font.setPointSize(12)
        username_label.setFont(label_font)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Kullanıcı adını gir")
        self.username_input.setFont(label_font)

        password_label = QLabel("Şifre")
        password_label.setFont(label_font)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Şifreyi gir")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(label_font)

        login_button = QPushButton("Giriş")
        login_button.setFont(label_font)
        login_button.clicked.connect(self._handle_login)

        form_layout.addWidget(title, 0, 0, 1, 2)
        form_layout.addWidget(username_label, 1, 0)
        form_layout.addWidget(self.username_input, 1, 1)
        form_layout.addWidget(password_label, 2, 0)
        form_layout.addWidget(self.password_input, 2, 1)
        form_layout.addWidget(login_button, 3, 0, 1, 2)

        outer_layout.addWidget(card)
        return page

    def _create_home_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)

        welcome_label = QLabel("Giriş başarılı. Ana uygulamaya hoş geldin.")
        welcome_font = QFont()
        welcome_font.setPointSize(14)
        welcome_label.setFont(welcome_font)
        welcome_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome_label)

        tabs = QTabWidget()
        tab_font = QFont()
        tab_font.setPointSize(12)
        tabs.setFont(tab_font)
        tabs.addTab(Catagory_Tab(), "Kategoriler")
        tabs.addTab(Product_Tab(), "Ürünler")
        tabs.addTab(Order_Tab(), "Siparişler")
        tabs.addTab(Profile_Tab(), "Profil")

        layout.addWidget(tabs)
        return page

    def _handle_login(self):
        entered_username = self.username_input.text().strip()
        entered_password = self.password_input.text()

        if entered_username == self._username and entered_password == self._password:
            self.stack.setCurrentWidget(self.home_page)
            return

        QMessageBox.warning(self, "Hatalı giriş", "Kullanıcı adı veya şifre yanlış.")


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = Main_Window()
    window.show()
    sys.exit(app.exec_())

