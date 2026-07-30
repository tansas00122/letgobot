def extract_item_links(page) -> list:
    logging.info("Letgo arama sayfasına gidiliyor...")
    try:
        # Doğrudan config içindeki veya direkt arama URL'sine gidiyoruz
        search_page_url = getattr(config, "SEARCH_URL", "https://www.letgo.com/tr_g1153/q-Logitech-G300s")
        page.goto(search_page_url, wait_until="domcontentloaded", timeout=config.PAGE_LOAD_TIMEOUT)
    except Exception as e:
        logging.error(f"Sayfa yüklenme hatası: {e}")
        pass
     
    page.wait_for_timeout(5000)

    try:
        page.click("button:has-text('Kabul Et')", timeout=3000)
    except Exception:
        pass

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
