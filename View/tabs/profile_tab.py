
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import (
    QApplication,
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
    def __init__(self, auth_model=None):
        super().__init__()
        self.auth_model = auth_model
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

        self.business_name = QLineEdit("North Pier Cafe")
        self.owner_name = QLineEdit("Admin Manager")
        self.email = QLineEdit("owner@northpier.example")
        self.phone = QLineEdit("+90 555 010 22 44")
        self.address = QTextEdit("Kemeralti Street No: 14, Izmir")
        self.address.setFixedHeight(76)
        self.hours = QLineEdit("09:00 - 23:00")

        form.addRow("Business name", self.business_name)
        form.addRow("Owner name", self.owner_name)
        form.addRow("Email", self.email)
        form.addRow("Phone", self.phone)
        form.addRow("Address", self.address)
        form.addRow("Opening hours", self.hours)
        layout.addLayout(form)

        actions = QHBoxLayout()
        save_button = make_button("Save Profile", "primary")
        save_button.clicked.connect(self._save_profile)
        actions.addWidget(save_button)
        actions.addStretch(1)
        actions.addWidget(make_badge("PUT /business/auth/edit", "accent"))
        layout.addLayout(actions)

        self.profile_status = make_label("Business name, email, and QR base URL can be saved to backend.", "muted")
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
                "The API should return this unique URL; the desktop client displays it for preview and printing.",
                "subtitle",
            )
        )

        self.menu_url = QLineEdit("https://qr-menu.example/north-pier")
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
        open_button = make_button("Preview Menu", "primary")
        open_button.clicked.connect(self._open_menu)
        actions.addWidget(copy_button)
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

    def _copy_url(self):
        QApplication.clipboard().setText(self.menu_url.text())
        self.qr_status.setText("Menu URL copied to clipboard.")

    def _open_menu(self):
        QDesktopServices.openUrl(QUrl(self.menu_url.text()))
        self.qr_status.setText("Menu preview opened in the default browser.")

    def _save_profile(self):
        if self.auth_model and self.auth_model.is_authenticated:
            try:
                self.auth_model.update_business(
                    name=self.business_name.text().strip(),
                    email=self.email.text().strip(),
                    qr_base_url=self.menu_url.text().strip(),
                )
            except ApiError as exc:
                QMessageBox.warning(self, "Profile save failed", str(exc))
                return
            self.profile_status.setText(f"Saved {self.business_name.text()} to backend.")
        else:
            self.profile_status.setText(f"Saved {self.business_name.text()} locally.")
        self._refresh_qr()
