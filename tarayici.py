import json
import logging
import signal
import time
from pathlib import Path
from typing import Set
from urllib.parse import urlsplit, urlunsplit

import requests
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

stop_requested = False


def request_stop(_signum, _frame):
    global stop_requested
    stop_requested = True
    logger.info("Kapatma sinyali alındı; mevcut tur tamamlanıyor.")


def normalize_url(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path.rstrip("/"), "", ""))


def load_seen_urls() -> Set[str]:
    path = config.SEEN_FILE_PATH
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return {normalize_url(url) for url in data if isinstance(url, str)}
        logger.warning("Hafıza dosyası liste formatında değil; boş başlatılıyor.")
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Hafıza dosyası okunamadı: %s", exc)
    return set()


def save_seen_urls(seen_urls: Set[str]) -> None:
    path: Path = config.SEEN_FILE_PATH
    temp_path = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path.write_text(
            json.dumps(sorted(seen_urls), ensure_ascii=False, indent=2), encoding="utf-8"
        )
        temp_path.replace(path)  # Atomik yazma: çökmede JSON bozulmaz.
    except OSError as exc:
        logger.error("Hafıza kaydedilemedi: %s", exc)


def send_to_webhook(session: requests.Session, item_url: str) -> bool:
