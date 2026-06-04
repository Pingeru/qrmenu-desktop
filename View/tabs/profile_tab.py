
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QDesktopServices, QPainter, QPixmap
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from models.api_client import ApiError
from utils.config import PUBLIC_MENU_BASE_URL

try:
    from view.components import (
        SectionHeader,
        make_button,
        make_card,
        make_label,
        make_scroll_area,
    )
except ModuleNotFoundError:
    from components import (
        SectionHeader,
        make_button,
        make_card,
        make_label,
        make_scroll_area,
    )


class Profile_Tab(QWidget):
    def __init__(self, auth_model=None, qr_controller=None, on_account_deleted=None):
        super().__init__()
        self.auth_model = auth_model
        self.qr_controller = qr_controller
        self.on_account_deleted = on_account_deleted
        self.qr_png_bytes = b""
        self.qr_pixmap = QPixmap()
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(18)

        root.addWidget(
            SectionHeader(
                "Business Profile & QR",
                "Edit profile data and preview the customer menu entry point from the desktop client.",
            )
        )

        content = QHBoxLayout()
        content.setSpacing(16)
        content.addWidget(self._build_profile_form(), 3)
        content.addWidget(self._build_qr_panel(), 2)
        root.addLayout(content, 1)

        self._load_business_profile()
        self._load_backend_qr(show_error=False)

    def _build_profile_form(self):
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        layout.addWidget(make_label("Profile Information", "section-title"))

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form.setRowWrapPolicy(QFormLayout.WrapLongRows)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)

        self.business_name = QLineEdit()
        self.email = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password_confirm = QLineEdit()
        self.password_confirm.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("Leave blank to keep current password")
        self.password_confirm.setPlaceholderText("Repeat new password")
        for field in [self.business_name, self.email, self.password, self.password_confirm]:
            field.setMinimumWidth(0)
            field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        form.addRow("Business name", self.business_name)
        form.addRow("Email", self.email)
        form.addRow("New password", self.password)
        form.addRow("Confirm password", self.password_confirm)
        layout.addLayout(form)

        actions = QHBoxLayout()
        save_button = make_button("Save Profile", "primary")
        save_button.clicked.connect(self._save_profile)
        delete_button = make_button("Delete Account", "danger")
        delete_button.clicked.connect(self._delete_account)
        actions.addWidget(save_button)
        actions.addWidget(delete_button)
        actions.addStretch(1)
        layout.addLayout(actions)

        self.profile_status = make_label("", "muted")
        self.profile_status.setWordWrap(True)
        layout.addWidget(self.profile_status)
        layout.addStretch(1)
        return make_scroll_area(card)

    def _build_qr_panel(self):
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        layout.addWidget(make_label("QR Menu Preview", "section-title"))

        self.menu_url = QLineEdit(card)
        self.menu_url.setReadOnly(True)
        self.menu_url.setPlaceholderText("Public menu URL is available after login")
        self.menu_url.setToolTip("The backend QR encodes this public menu URL.")
        self.menu_url.hide()

        qr_frame = make_card()
        qr_layout = QVBoxLayout(qr_frame)
        qr_layout.setContentsMargins(18, 18, 18, 18)
        qr_layout.setAlignment(Qt.AlignCenter)
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setMinimumSize(188, 188)
        qr_layout.addWidget(self.qr_label)
        layout.addWidget(qr_frame)

        actions = QGridLayout()
        actions.setHorizontalSpacing(8)
        actions.setVerticalSpacing(8)
        refresh_button = make_button("Refresh QR", "primary")
        refresh_button.clicked.connect(lambda: self._load_backend_qr(show_error=True))
        copy_button = make_button("Copy URL")
        copy_button.clicked.connect(self._copy_url)
        save_qr_button = make_button("Save PNG")
        save_qr_button.clicked.connect(self._save_qr_png)
        print_qr_button = make_button("Print QR")
        print_qr_button.clicked.connect(self._print_qr)
        open_button = make_button("Preview Menu")
        open_button.clicked.connect(self._open_menu)
        actions.addWidget(refresh_button, 0, 0)
        actions.addWidget(copy_button, 0, 1)
        actions.addWidget(save_qr_button, 0, 2)
        actions.addWidget(print_qr_button, 1, 0)
        actions.addWidget(open_button, 1, 1, 1, 2)
        layout.addLayout(actions)

        self.qr_status = make_label("", "muted")
        self.qr_status.setWordWrap(True)
        layout.addWidget(self.qr_status)
        layout.addStretch(1)
        return card

    def _load_business_profile(self):
        business = self.auth_model.business if self.auth_model else None
        if not business:
            return

        self.business_name.setText(business.get("name") or "")
        self.email.setText(business.get("email") or "")
        self.menu_url.setText(self._business_menu_url())

    def _business_id(self):
        business = self.auth_model.business if self.auth_model else None
        if not business:
            return ""
        return str(business.get("_id") or business.get("id") or "")

    def _business_menu_url(self):
        business_id = self._business_id()
        if not business_id:
            return ""
        return f"{PUBLIC_MENU_BASE_URL.rstrip('/')}/{business_id}"

    def _load_backend_qr(self, show_error=False):
        if not hasattr(self, "qr_label"):
            return
        if not self.auth_model or not self.auth_model.is_authenticated:
            self.qr_status.setText("Login is required before loading the backend QR.")
            return
        if not self.qr_controller:
            self.qr_status.setText("QR API controller is not available.")
            return

        self.menu_url.setText(self._business_menu_url())
        try:
            qr_png_bytes = self.qr_controller.load_business_qr()
        except ApiError as exc:
            self.qr_png_bytes = b""
            self.qr_pixmap = QPixmap()
            self.qr_label.clear()
            self.qr_status.setText(f"Could not load backend QR: {exc}")
            if show_error:
                QMessageBox.warning(self, "QR load failed", str(exc))
            return

        pixmap = QPixmap()
        if not pixmap.loadFromData(qr_png_bytes, "PNG"):
            self.qr_png_bytes = b""
            self.qr_pixmap = QPixmap()
            self.qr_label.clear()
            self.qr_status.setText("Backend QR response could not be decoded as PNG.")
            if show_error:
                QMessageBox.warning(self, "QR load failed", "Backend QR response could not be decoded as PNG.")
            return

        self.qr_png_bytes = qr_png_bytes
        self.qr_pixmap = pixmap
        self._show_qr_pixmap()
        self.qr_status.setText("")

    def _show_qr_pixmap(self):
        if self.qr_pixmap.isNull():
            self.qr_label.clear()
            return
        self.qr_label.setPixmap(
            self.qr_pixmap.scaled(188, 188, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def _current_qr_pixmap(self, size=720):
        if self.qr_pixmap.isNull():
            return QPixmap()
        return self.qr_pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def _copy_url(self):
        if not self.menu_url.text():
            self.qr_status.setText("Public menu URL is not available yet.")
            return
        QApplication.clipboard().setText(self.menu_url.text())
        self.qr_status.setText("Menu URL copied to clipboard.")

    def _open_menu(self):
        if not self.menu_url.text():
            self.qr_status.setText("Public menu URL is not available yet.")
            return
        QDesktopServices.openUrl(QUrl(self.menu_url.text()))
        self.qr_status.setText("Menu preview opened in the default browser.")

    def _save_qr_png(self):
        if not self.qr_png_bytes:
            QMessageBox.warning(self, "QR save failed", "Load the backend QR before saving.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save QR PNG",
            "qr-menu.png",
            "PNG Images (*.png)",
        )
        if not path:
            return
        if not path.lower().endswith(".png"):
            path = f"{path}.png"
        try:
            with open(path, "wb") as output:
                output.write(self.qr_png_bytes)
        except OSError as exc:
            QMessageBox.warning(self, "QR save failed", str(exc))
            return
        if self.qr_png_bytes:
            self.qr_status.setText(f"QR saved to {path}.")
        else:
            QMessageBox.warning(self, "QR save failed", "The QR PNG could not be saved.")

    def _print_qr(self):
        if self.qr_pixmap.isNull():
            QMessageBox.warning(self, "QR print failed", "Load the backend QR before printing.")
            return
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() != QDialog.Accepted:
            return

        pixmap = self._current_qr_pixmap(720)
        painter = QPainter()
        if not painter.begin(printer):
            QMessageBox.warning(self, "QR print failed", "The printer could not be opened.")
            return

        viewport = painter.viewport()
        scaled_size = pixmap.size()
        scaled_size.scale(viewport.size(), Qt.KeepAspectRatio)
        painter.setViewport(
            viewport.x(),
            viewport.y(),
            scaled_size.width(),
            scaled_size.height(),
        )
        painter.setWindow(pixmap.rect())
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        self.qr_status.setText("QR sent to printer.")

    def _save_profile(self):
        if self.auth_model and self.auth_model.is_authenticated:
            password = self.password.text()
            password_confirm = self.password_confirm.text()
            if password or password_confirm:
                if password != password_confirm:
                    QMessageBox.warning(self, "Profile save failed", "Passwords do not match.")
                    return
            try:
                fields = {
                    "name": self.business_name.text().strip(),
                    "email": self.email.text().strip(),
                }
                if password:
                    fields["password"] = password
                self.auth_model.update_business(**fields)
            except ApiError as exc:
                QMessageBox.warning(self, "Profile save failed", str(exc))
                return
            self.password.clear()
            self.password_confirm.clear()
            self.profile_status.setText(f"Saved {self.business_name.text()} to backend.")
        else:
            self.profile_status.setText("Login is required before profile data can be saved to backend.")
        self._load_business_profile()
        self._load_backend_qr(show_error=False)

    def _delete_account(self):
        if not self.auth_model or not self.auth_model.is_authenticated:
            self.profile_status.setText("Login is required before the backend account can be deleted.")
            return

        choice = QMessageBox.question(
            self,
            "Delete account",
            "This will delete the business account from qrmenu-api and log you out. Continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if choice != QMessageBox.Yes:
            return

        try:
            self.auth_model.delete_business()
        except ApiError as exc:
            QMessageBox.warning(self, "Account delete failed", str(exc))
            return

        self.profile_status.setText("Business account deleted from backend.")
        if self.on_account_deleted:
            self.on_account_deleted()
