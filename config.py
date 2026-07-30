import os
from pathlib import Path


def _positive_int(name: str, default: int) -> int:
    value = os.getenv(name, str(default))
    try:
        parsed = int(value)
    except ValueError:
        return default
    return parsed if parsed > 0 else default


# Required in Render's Environment settings.  Do not put the real URL in Git.
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "").strip()
WEBHOOK_TIMEOUT_SECONDS = _positive_int("WEBHOOK_TIMEOUT_SECONDS", 15)
CHECK_INTERVAL_SECONDS = _positive_int("CHECK_INTERVAL_SECONDS", 60)
RESTART_DELAY_SECONDS = _positive_int("RESTART_DELAY_SECONDS", 30)

SEARCH_URL = os.getenv(
    "SEARCH_URL", "https://www.letgo.com/tr_g1153/q-Logitech-G300s"
).strip()

# On Render this remains only for the lifetime of the container unless a
# persistent disk is mounted and SEEN_FILE_PATH points to that mount.
SEEN_FILE_PATH = Path(os.getenv("SEEN_FILE_PATH", "seen_urls.json"))

HEADLESS = os.getenv("HEADLESS", "true").lower() not in {"0", "false", "no"}
PAGE_LOAD_TIMEOUT_MS = _positive_int("PAGE_LOAD_TIMEOUT_MS", 60_000)
VIEWPORT = {"width": 1280, "height": 800}
USER_AGENT = os.getenv(
    "USER_AGENT",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
)
