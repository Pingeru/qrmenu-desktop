
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QDesktopServices, QPainter
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from models.api_client import ApiError

try:
    from view.components import (
        SectionHeader,
        build_qr_pixmap,
        make_badge,
        make_button,
        make_card,
        make_label,
    )
except ModuleNotFoundError:
    from components import (
        SectionHeader,
        build_qr_pixmap,
        make_badge,
        make_button,
        make_card,
        make_label,
    )


class Profile_Tab(QWidget):
    def __init__(self, auth_model=None, on_account_deleted=None):
        super().__init__()
        self.auth_model = auth_model
        self.on_account_deleted = on_account_deleted
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
        self._refresh_qr()

    def _build_profile_form(self):
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        layout.addWidget(make_label("Profile Information", "section-title"))

        form = QFormLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)

        self.business_name = QLineEdit()
        self.owner_name = QLineEdit()
        self.email = QLineEdit()
        self.phone = QLineEdit()
        self.address = QTextEdit()
        self.address.setFixedHeight(76)
        self.hours = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password_confirm = QLineEdit()
        self.password_confirm.setEchoMode(QLineEdit.Password)

        for field in [self.owner_name, self.phone, self.address, self.hours]:
            field.setEnabled(False)
            field.setToolTip("qrmenu-api does not expose this business profile field yet.")

        self.owner_name.setPlaceholderText("Endpoint pending")
        self.phone.setPlaceholderText("Endpoint pending")
        self.address.setPlaceholderText("Endpoint pending")
        self.hours.setPlaceholderText("Endpoint pending")
        self.password.setPlaceholderText("Leave blank to keep current password")
        self.password_confirm.setPlaceholderText("Repeat new password")

        form.addRow("Business name", self.business_name)
        form.addRow("Owner name", self.owner_name)
        form.addRow("Email", self.email)
        form.addRow("Phone", self.phone)
        form.addRow("Address", self.address)
        form.addRow("Opening hours", self.hours)
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
        actions.addWidget(make_badge("PUT/DELETE /business/auth", "accent"))
        layout.addLayout(actions)

        self.profile_status = make_label(
            "Business name, email, password, and account deletion are connected to qrmenu-api. "
            "QR URL preview is local until the backend exposes a profile URL field.",
            "muted",
        )
        self.profile_status.setWordWrap(True)
        layout.addWidget(self.profile_status)
        layout.addStretch(1)
        return card

    def _build_qr_panel(self):
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        layout.addWidget(make_label("QR Menu Preview", "section-title"))
        layout.addWidget(
            make_label(
                "Enter the menu URL that the QR should encode, then save or print the generated QR.",
                "subtitle",
            )
        )

        self.menu_url = QLineEdit()
        self.menu_url.setPlaceholderText("https://qrmenu.dovanay.com/menu/your-business")
        self.menu_url.textChanged.connect(self._refresh_qr)
        layout.addWidget(self.menu_url)

        qr_frame = make_card()
        qr_layout = QVBoxLayout(qr_frame)
        qr_layout.setContentsMargins(18, 18, 18, 18)
        qr_layout.setAlignment(Qt.AlignCenter)
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignCenter)
        qr_layout.addWidget(self.qr_label)
        layout.addWidget(qr_frame)

        actions = QHBoxLayout()
        copy_button = make_button("Copy URL")
        copy_button.clicked.connect(self._copy_url)
        save_qr_button = make_button("Save PNG")
        save_qr_button.clicked.connect(self._save_qr_png)
        print_qr_button = make_button("Print QR")
        print_qr_button.clicked.connect(self._print_qr)
        open_button = make_button("Preview Menu", "primary")
        open_button.clicked.connect(self._open_menu)
        actions.addWidget(copy_button)
        actions.addWidget(save_qr_button)
        actions.addWidget(print_qr_button)
        actions.addWidget(open_button)
        layout.addLayout(actions)

        self.qr_status = make_label("QR preview generated from the current menu URL.", "muted")
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
        qr_base_url = business.get("qr_base_url")
        if qr_base_url:
            self.menu_url.setText(qr_base_url)
        self.profile_status.setText("Business profile loaded from backend login response.")

    def _refresh_qr(self):
        if hasattr(self, "qr_label"):
            self.qr_label.setPixmap(build_qr_pixmap(self.menu_url.text(), 188))

    def _current_qr_pixmap(self, size=360):
        return build_qr_pixmap(self.menu_url.text(), size)

    def _copy_url(self):
        QApplication.clipboard().setText(self.menu_url.text())
        self.qr_status.setText("Menu URL copied to clipboard.")

    def _open_menu(self):
        QDesktopServices.openUrl(QUrl(self.menu_url.text()))
        self.qr_status.setText("Menu preview opened in the default browser.")

    def _save_qr_png(self):
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
        if self._current_qr_pixmap().save(path, "PNG"):
            self.qr_status.setText(f"QR saved to {path}.")
        else:
            QMessageBox.warning(self, "QR save failed", "The QR PNG could not be saved.")

    def _print_qr(self):
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
        self._refresh_qr()

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
