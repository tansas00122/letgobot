import os
from pathlib import Path


def _positive_int(name: str, default: int) -> int:
    value = os.getenv(name, str(default))
    try:
        parsed = int(value)
        return parsed if parsed > 0 else default
    except (TypeError, ValueError):
        return default


# Render > Environment Variables bölümünden ekleyin.
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "").strip()

# Tarama ayarları
SEARCH_URL = os.getenv(
    "SEARCH_URL",
    "https://www.letgo.com/tr_g1153/q-Logitech-G300s",
).strip()

CHECK_INTERVAL_SECONDS = _positive_int("CHECK_INTERVAL_SECONDS", 60)
WEBHOOK_TIMEOUT_SECONDS = _positive_int("WEBHOOK_TIMEOUT_SECONDS", 15)
RESTART_DELAY_SECONDS = _positive_int("RESTART_DELAY_SECONDS",
