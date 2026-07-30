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
    return url
