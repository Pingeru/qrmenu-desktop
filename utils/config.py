"""Shared configuration values."""

import os


API_BASE_URL = os.getenv("QRMENU_API_BASE_URL", "http://localhost:3005/api/v1")
API_TIMEOUT_SECONDS = float(os.getenv("QRMENU_API_TIMEOUT_SECONDS", "10"))
