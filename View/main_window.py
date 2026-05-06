import sys

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtCore import Qt

try:
    from view.components import app_stylesheet, make_badge, make_button, make_card, make_label
    from view.tabs.analytics_tab import Analytics_Tab
    from view.tabs.category_tab import Catagory_Tab
    from view.tabs.order_tab import Order_Tab
    from view.tabs.product_tab import Product_Tab
    from view.tabs.profile_tab import Profile_Tab
except ModuleNotFoundError:
    from components import app_stylesheet, make_badge, make_button, make_card, make_label
    from tabs.analytics_tab import Analytics_Tab
    from tabs.category_tab import Catagory_Tab
    from tabs.order_tab import Order_Tab
    from tabs.product_tab import Product_Tab
    from tabs.profile_tab import Profile_Tab


class Main_Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QR Menu Builder")
        self.setGeometry(50, 50, 1300, 900)
        self.setMinimumSize(1100, 760)
        self.setStyleSheet(app_stylesheet())

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
        page.setObjectName("LoginPage")
        outer_layout = QVBoxLayout(page)
        outer_layout.setAlignment(Qt.AlignCenter)
        outer_layout.setContentsMargins(24, 24, 24, 24)

        card = make_card()
        card.setMaximumWidth(430)
        card.setMinimumWidth(390)
        form_layout = QGridLayout(card)
        form_layout.setContentsMargins(28, 28, 28, 28)
        form_layout.setHorizontalSpacing(14)
        form_layout.setVerticalSpacing(14)

        title = QLabel("QR Menu Builder")
        title.setAlignment(Qt.AlignCenter)
        title.setProperty("role", "title")
        title_font = QFont()
        title_font.setPointSize(22)
        title_font.setBold(True)
        title.setFont(title_font)

        subtitle = make_label("Business desktop client", "subtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        label_font = QFont()
        label_font.setPointSize(11)

        username_label = QLabel("Username")
        username_label.setFont(label_font)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("admin")
        self.username_input.setFont(label_font)

        password_label = QLabel("Password")
        password_label.setFont(label_font)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("1")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(label_font)

        login_button = make_button("Login", "primary")
        login_button.setFont(label_font)
        login_button.clicked.connect(self._handle_login)
        self.password_input.returnPressed.connect(self._handle_login)

        form_layout.addWidget(title, 0, 0, 1, 2)
        form_layout.addWidget(subtitle, 1, 0, 1, 2)
        form_layout.addWidget(username_label, 2, 0)
        form_layout.addWidget(self.username_input, 2, 1)
        form_layout.addWidget(password_label, 3, 0)
        form_layout.addWidget(self.password_input, 3, 1)
        form_layout.addWidget(login_button, 4, 0, 1, 2)

        outer_layout.addWidget(card)
        return page

    def _create_home_page(self):
        page = QWidget()
        page.setObjectName("HomePage")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(22, 18, 22, 22)
        layout.setSpacing(14)

        header = QFrame()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)

        title = QLabel("QR Menu Builder")
        title.setProperty("role", "title")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)

        header_layout.addWidget(title)
        header_layout.addWidget(make_badge("Demo API client", "accent"))
        header_layout.addStretch(1)
        header_layout.addWidget(make_label("Logged in as admin", "muted"))

        logout_button = make_button("Logout", "ghost")
        logout_button.clicked.connect(self._handle_logout)
        header_layout.addWidget(logout_button)
        layout.addWidget(header)

        tabs = QTabWidget()
        tab_font = QFont()
        tab_font.setPointSize(11)
        tab_font.setBold(True)
        tabs.setFont(tab_font)
        tabs.addTab(Catagory_Tab(), "Categories")
        tabs.addTab(Product_Tab(), "Products")
        tabs.addTab(Order_Tab(), "Live Orders")
        tabs.addTab(Profile_Tab(), "Profile && QR")
        tabs.addTab(Analytics_Tab(), "Analytics")

        layout.addWidget(tabs, 1)
        return page

    def _handle_login(self):
        entered_username = self.username_input.text().strip()
        entered_password = self.password_input.text()

        if entered_username == self._username and entered_password == self._password:
            self.stack.setCurrentWidget(self.home_page)
            return

        QMessageBox.warning(self, "Login failed", "Username or password is incorrect.")

    def _handle_logout(self):
        self.password_input.clear()
        self.stack.setCurrentWidget(self.login_page)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Main_Window()
    window.show()
    sys.exit(app.exec_())
