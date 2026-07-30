import json
import logging
import os
import time
import requests
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

def load_seen_urls() -> set:
    if not os.path.exists(config.SEEN_FILE_PATH):
        return set()
    try:
        with open(config.SEEN_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data) if isinstance(data, list) else set()
    except Exception:
        return set()

def save_seen_urls(seen_set: set):
    try:
        with open(config.SEEN_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(list(seen_set), f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Kayıt hatası: {e}")

def send_to_webhook(item_url: str) -> bool:
    payload = {"source": "Letgo", "search_query": "Logitech G300s", "link": item_url}
    try:
        res = requests.post(config.WEBHOOK_URL, json=payload, timeout=config.WEBHOOK_TIMEOUT_SECONDS)
        if res.status_code == 200:
            logging.info(f"✅ Webhook'a gönderildi: {item_url}")
            return True
        return False
    except Exception as e:
        logging.error(f"❌ Webhook hatası: {e}")
        return False

def extract_item_links(page) -> list:
    logging.info("Letgo ana sayfasına gidiliyor...")
    try:
        page.goto("https://www.letgo.com", wait_until="domcontentloaded", timeout=config.PAGE_LOAD_TIMEOUT)
    except Exception:
        pass
    
    page.wait_for_timeout(5000)

    try:
        page.click("button:has-text('Kabul Et')", timeout=3000)
    except Exception:
        pass

    try:
        logging.info("Arama yapılıyor: Logitech G300s")
        search_input = page.locator("input[data-aut-id='searchBoxText'], input[type='text']").first
        search_input.click()
        search_input.fill("Logitech G300s")
        page.keyboard.press("Enter")
        
        page.wait_for_timeout(7000)
    except Exception as e:
        logging.error(f"Arama kutusu etkileşim hatası: {e}")
        page.goto(config.SEARCH_URL, wait_until="domcontentloaded", timeout=config.PAGE_LOAD_TIMEOUT)
        page.wait_for_timeout(5000)

    for _ in range(3):
        page.keyboard.press("PageDown")
        page.wait_for_timeout(1500)

    raw_links = page.evaluate("""
        () => Array.from(document.querySelectorAll('a'))
            .map(a => a.href)
            .filter(href => href && (href.includes('/item/') || href.includes('/i/') || href.includes('/ilan/')))
    """)

    cleaned_links = list(set([link.split("?")[0] for link in raw_links if link]))
    logging.info(f"Sayfada toplam {len(cleaned_links)} adet ilan tespit edildi.")
    return cleaned_links

def start_bot():
    seen_urls = load_seen_urls()
    logging.info(f"🚀 Bot Başlatıldı. Hafıza: {len(seen_urls)}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=config.HEADLESS,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            user_agent=config.USER_AGENT,
            viewport=config.VIEWPORT,
            locale="tr-TR"
        )
        page = context.new_page()

        while True:
            try:
                current_links = extract_item_links(page)
                has_new_item = False

                for link in current_links:
                    if link not in seen_urls:
                        logging.info(f"🔥 YENİ İLAN: {link}")
                        send_to_webhook(link)
                        seen_urls.add(link)
                        has_new_item = True
                        time.sleep(1)

                if has_new_item:
                    save_seen_urls(seen_urls)
                else:
                    logging.info("Yeni ilan bulunamadı.")

            except Exception as e:
                logging.error(f"Döngü hatası: {e}")

            logging.info(f"⏳ {config.CHECK_INTERVAL_SECONDS} saniye bekleniyor...\n")
            time.sleep(config.CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    start_bot()
