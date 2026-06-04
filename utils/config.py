"""Shared configuration values."""

import os


API_BASE_URL = os.getenv("QRMENU_API_BASE_URL", "https://qrmenu.dovanay.com/api/v1")
API_TIMEOUT_SECONDS = float(os.getenv("QRMENU_API_TIMEOUT_SECONDS", "10"))
PUBLIC_MENU_BASE_URL = os.getenv("QRMENU_PUBLIC_MENU_BASE_URL", "https://qrmenu.dovanay.com/menu")
