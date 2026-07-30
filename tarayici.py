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
        logging.info("Arama yapılıyor: iPhone 13")
        # Arama çubuğunu bulup arama kelimesini yazalım ve Enter'a basalım
        search_input = page.locator("input[data-aut-id='searchBoxText'], input[type='text']").first
        search_input.click()
        search_input.fill("iPhone 13")
        page.keyboard.press("Enter")
        
        # Sonuçların yüklenmesini bekleyelim
        page.wait_for_timeout(7000)
    except Exception as e:
        logging.error(f"Arama kutusu etkileşim hatası: {e}")
        # Hata olursa doğrudan arama URL'sine fallback yapalım
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
