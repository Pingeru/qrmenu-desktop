import sys
from pathlib import Path

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

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from controllers.analytics_controller import AnalyticsController
from controllers.category_controller import CategoryController
from controllers.order_controller import OrderController
from controllers.product_controller import ProductController
from controllers.qr_controller import QrController
from models.api_client import ApiClient, ApiError
from models.analytics_model import AnalyticsModel
from models.auth_model import AuthModel
from models.category_model import CategoryModel
from models.order_model import OrderModel
from models.product_model import ProductModel
from models.qr_model import QrModel
from utils.config import API_BASE_URL

try:
    from view.components import app_stylesheet, make_badge, make_button, make_card
    from view.tabs.analytics_tab import Analytics_Tab
    from view.tabs.category_tab import Catagory_Tab
    from view.tabs.order_tab import Order_Tab
    from view.tabs.product_tab import Product_Tab
    from view.tabs.profile_tab import Profile_Tab
except ModuleNotFoundError:
    from components import app_stylesheet, make_badge, make_button, make_card
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

        self.api_client = ApiClient()
        self.api_client.set_base_url(API_BASE_URL)
        self.auth_model = AuthModel(self.api_client)
        self.analytics_controller = AnalyticsController(AnalyticsModel(self.api_client))
        self.category_controller = CategoryController(CategoryModel(self.api_client))
        self.order_controller = OrderController(OrderModel(self.api_client))
        self.product_controller = ProductController(ProductModel(self.api_client))
        self.qr_controller = QrController(QrModel(self.api_client))

        self.stack = QStackedWidget()
        self.login_page = self._create_login_page()
        self.register_page = self._create_register_page()
        self.home_page = None

        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.register_page)
        self.setCentralWidget(self.stack)

    def _create_login_page(self):
        page = QWidget()
        page.setObjectName("LoginPage")
        outer_layout = QVBoxLayout(page)
        outer_layout.setAlignment(Qt.AlignCenter)
        outer_layout.setContentsMargins(24, 24, 24, 24)

        card = make_card("AuthCard")
        card.setMaximumWidth(560)
        card.setMinimumWidth(460)
        form_layout = QGridLayout(card)
        form_layout.setContentsMargins(34, 32, 34, 32)
        form_layout.setHorizontalSpacing(14)
        form_layout.setVerticalSpacing(15)

        brand_mark = QLabel("QM")
        brand_mark.setObjectName("AuthMark")
        brand_mark.setAlignment(Qt.AlignCenter)
        brand_mark.setFixedSize(42, 42)

        title = QLabel("QR Menu Builder")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("AuthTitle")
        title_font = QFont()
        title_font.setPointSize(23)
        title_font.setBold(True)
        title.setFont(title_font)

        label_font = QFont()
        label_font.setPointSize(11)

        email_label = QLabel("Email")
        email_label.setFont(label_font)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("business@example.com")
        self.email_input.setFont(label_font)

        password_label = QLabel("Password")
        password_label.setFont(label_font)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(label_font)

        login_button = make_button("Login", "primary")
        login_button.setFont(label_font)
        login_button.clicked.connect(self._handle_login)
        self.password_input.returnPressed.connect(self._handle_login)

        register_button = make_button("Create Business Account", "ghost")
        register_button.setFont(label_font)
        register_button.clicked.connect(self._show_register_page)

        form_layout.addWidget(brand_mark, 0, 0, 1, 2, Qt.AlignCenter)
        form_layout.addWidget(title, 1, 0, 1, 2)
        form_layout.addWidget(email_label, 3, 0)
        form_layout.addWidget(self.email_input, 3, 1)
        form_layout.addWidget(password_label, 4, 0)
        form_layout.addWidget(self.password_input, 4, 1)
        form_layout.addWidget(login_button, 5, 0, 1, 2)
        form_layout.addWidget(register_button, 6, 0, 1, 2)

        outer_layout.addWidget(card)
        return page

    def _create_register_page(self):
        page = QWidget()
        page.setObjectName("LoginPage")
        outer_layout = QVBoxLayout(page)
        outer_layout.setAlignment(Qt.AlignCenter)
        outer_layout.setContentsMargins(24, 24, 24, 24)

        card = make_card("AuthCard")
        card.setMaximumWidth(620)
        card.setMinimumWidth(500)
        form_layout = QGridLayout(card)
        form_layout.setContentsMargins(34, 32, 34, 32)
        form_layout.setHorizontalSpacing(14)
        form_layout.setVerticalSpacing(15)

        brand_mark = QLabel("QM")
        brand_mark.setObjectName("AuthMark")
        brand_mark.setAlignment(Qt.AlignCenter)
        brand_mark.setFixedSize(42, 42)

        title = QLabel("Create Business Account")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("AuthTitle")
        title_font = QFont()
        title_font.setPointSize(23)
        title_font.setBold(True)
        title.setFont(title_font)

        subtitle = QLabel("Create your workspace and start building the QR menu.")
        subtitle.setObjectName("AuthSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        label_font = QFont()
        label_font.setPointSize(11)

        name_label = QLabel("Business name")
        name_label.setFont(label_font)
        self.register_name_input = QLineEdit()
        self.register_name_input.setPlaceholderText("North Pier Cafe")
        self.register_name_input.setFont(label_font)

        email_label = QLabel("Email")
        email_label.setFont(label_font)
        self.register_email_input = QLineEdit()
        self.register_email_input.setPlaceholderText("owner@example.com")
        self.register_email_input.setFont(label_font)

        password_label = QLabel("Password")
        password_label.setFont(label_font)
        self.register_password_input = QLineEdit()
        self.register_password_input.setEchoMode(QLineEdit.Password)
        self.register_password_input.setPlaceholderText("Password")
        self.register_password_input.setFont(label_font)

        confirm_label = QLabel("Confirm password")
        confirm_label.setFont(label_font)
        self.register_confirm_input = QLineEdit()
        self.register_confirm_input.setEchoMode(QLineEdit.Password)
        self.register_confirm_input.setPlaceholderText("Repeat password")
        self.register_confirm_input.setFont(label_font)

        create_button = make_button("Create Account", "primary")
        create_button.setFont(label_font)
        create_button.clicked.connect(self._handle_register)
        self.register_confirm_input.returnPressed.connect(self._handle_register)

        back_button = make_button("Back to Login", "ghost")
        back_button.setFont(label_font)
        back_button.clicked.connect(self._show_login_page)

        form_layout.addWidget(brand_mark, 0, 0, 1, 2, Qt.AlignCenter)
        form_layout.addWidget(title, 1, 0, 1, 2)
        form_layout.addWidget(subtitle, 2, 0, 1, 2)
        form_layout.addWidget(name_label, 3, 0)
        form_layout.addWidget(self.register_name_input, 3, 1)
        form_layout.addWidget(email_label, 4, 0)
        form_layout.addWidget(self.register_email_input, 4, 1)
        form_layout.addWidget(password_label, 5, 0)
        form_layout.addWidget(self.register_password_input, 5, 1)
        form_layout.addWidget(confirm_label, 6, 0)
        form_layout.addWidget(self.register_confirm_input, 6, 1)
        form_layout.addWidget(create_button, 7, 0)
        form_layout.addWidget(back_button, 7, 1)

        outer_layout.addWidget(card)
        return page

    def _create_home_page(self):
        page = QWidget()
        page.setObjectName("HomePage")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(22, 18, 22, 22)
        layout.setSpacing(14)

        header = QFrame()
        header.setObjectName("AppHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(18, 14, 18, 14)
        header_layout.setSpacing(14)

        brand_mark = QLabel("QM")
        brand_mark.setObjectName("BrandMark")
        brand_mark.setAlignment(Qt.AlignCenter)
        brand_mark.setFixedSize(34, 34)

        title = QLabel("QR Menu Builder")
        title.setObjectName("HeaderTitle")

        subtitle = QLabel("Menu operations connected to qrmenu-api")
        subtitle.setObjectName("HeaderSubtitle")

        title_group = QVBoxLayout()
        title_group.setSpacing(1)
        title_group.addWidget(title)
        title_group.addWidget(subtitle)

        header_layout.addWidget(brand_mark)
        header_layout.addLayout(title_group)
        header_layout.addWidget(make_badge("Backend API", "dark"))
        header_layout.addStretch(1)
        business = self.auth_model.business or {}
        business_label = business.get("name") or business.get("email") or "business"
        business_badge = make_badge(f"Logged in as {business_label}", "accent")
        header_layout.addWidget(business_badge)

        logout_button = make_button("Logout", "ghost")
        logout_button.clicked.connect(self._handle_logout)
        header_layout.addWidget(logout_button)
        layout.addWidget(header)

        tabs = QTabWidget()
        tab_font = QFont()
        tab_font.setPointSize(11)
        tab_font.setBold(True)
        tabs.setFont(tab_font)
        self.category_tab = Catagory_Tab(
            category_controller=self.category_controller,
            product_controller=self.product_controller,
            auth_model=self.auth_model,
            on_categories_changed=self._handle_categories_changed,
        )
        self.product_tab = Product_Tab(
            product_controller=self.product_controller,
            category_controller=self.category_controller,
            auth_model=self.auth_model,
        )
        tabs.addTab(self.category_tab, "Categories")
        tabs.addTab(self.product_tab, "Products")
        tabs.addTab(Order_Tab(order_controller=self.order_controller), "Live Orders")
        tabs.addTab(
            Profile_Tab(
                auth_model=self.auth_model,
                qr_controller=self.qr_controller,
                on_account_deleted=self._handle_account_deleted,
            ),
            "Profile && QR",
        )
        tabs.addTab(
            Analytics_Tab(
                analytics_controller=self.analytics_controller,
                order_controller=self.order_controller,
            ),
            "Analytics",
        )
        tabs.currentChanged.connect(self._handle_tab_changed)

        layout.addWidget(tabs, 1)
        return page

    def _handle_login(self):
        entered_email = self.email_input.text().strip()
        entered_password = self.password_input.text()

        if not entered_email or not entered_password:
            QMessageBox.warning(self, "Login failed", "Email and password are required.")
            return

        self.api_client.set_base_url(API_BASE_URL)

        try:
            self.auth_model.login_business(entered_email, entered_password)
        except ApiError as exc:
            QMessageBox.warning(self, "Login failed", str(exc))
            return

        self._show_home_page()

    def _handle_register(self):
        name = self.register_name_input.text().strip()
        email = self.register_email_input.text().strip()
        password = self.register_password_input.text()
        password_confirm = self.register_confirm_input.text()

        if not name or not email or not password:
            QMessageBox.warning(self, "Register failed", "Business name, email, and password are required.")
            return

        if password != password_confirm:
            QMessageBox.warning(self, "Register failed", "Passwords do not match.")
            return

        self.api_client.set_base_url(API_BASE_URL)

        try:
            self.auth_model.register_business(name, email, password)
        except ApiError as exc:
            QMessageBox.warning(self, "Register failed", str(exc))
            return

        self.email_input.setText(email)
        self.password_input.clear()
        self._show_home_page()

    def _show_register_page(self):
        if not self.register_email_input.text().strip():
            self.register_email_input.setText(self.email_input.text().strip())
        self.stack.setCurrentWidget(self.register_page)

    def _show_login_page(self):
        self.stack.setCurrentWidget(self.login_page)

    def _show_home_page(self):
        if self.home_page is not None:
            self.stack.removeWidget(self.home_page)
            self.home_page.deleteLater()

        self.home_page = self._create_home_page()
        self.stack.addWidget(self.home_page)
        self.stack.setCurrentWidget(self.home_page)

    def _handle_logout(self):
        self.auth_model.logout()
        self.password_input.clear()
        self.register_password_input.clear()
        self.register_confirm_input.clear()
        self.stack.setCurrentWidget(self.login_page)

    def _handle_account_deleted(self):
        self.password_input.clear()
        self.register_password_input.clear()
        self.register_confirm_input.clear()
        if self.home_page is not None:
            self.stack.removeWidget(self.home_page)
            self.home_page.deleteLater()
            self.home_page = None
        self.stack.setCurrentWidget(self.login_page)

    def _handle_categories_changed(self):
        if hasattr(self, "product_tab"):
            self.product_tab.mark_backend_dirty()

    def _handle_tab_changed(self, index):
        tabs = self.sender()
        if tabs and hasattr(self, "product_tab") and tabs.widget(index) is self.product_tab:
            self.product_tab.refresh_from_backend()
        elif tabs and hasattr(self, "category_tab") and tabs.widget(index) is self.category_tab:
            self.category_tab.refresh_from_backend()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Main_Window()
    window.show()
    sys.exit(app.exec_())
