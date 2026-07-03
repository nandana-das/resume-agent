def fetch_jd_from_url(url: str) -> str:
    if os.getenv("FIRECRAWL_API_KEY"):
        try:
            text = scrape_with_firecrawl(url)
            if text and len(text) > 200:
                return text
        except:
            pass  # Fall through to httpx
    return scrape_with_httpx(url)