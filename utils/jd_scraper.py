import os
import json
import re

import httpx
from bs4 import BeautifulSoup

try:
    import streamlit as st
except Exception:
    st = None


def _clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "")
    return text.strip()


def _clean_text_preserve_lines(text: str) -> str:
    """Like _clean_text, but keeps line breaks intact — collapses only the
    horizontal whitespace within each line, plus blank/duplicate line runs."""
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in (text or "").splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines)


def _get_config_value(key: str):
    if st is not None:
        try:
            if key in st.secrets:
                value = st.secrets.get(key)
                if value:
                    return value
        except Exception:
            pass

    return os.getenv(key)


def _extract_jobposting_jsonld(soup: BeautifulSoup) -> str:
    """
    Prefer structured data when the page exposes a JobPosting schema.
    Many careers pages include the real posting here even when the visible DOM
    contains cookie/legal boilerplate.
    """
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = script.string or script.get_text(strip=True)
        if not raw:
            continue

        try:
            data = json.loads(raw)
        except Exception:
            continue

        candidates = data if isinstance(data, list) else [data]
        for item in candidates:
            if not isinstance(item, dict):
                continue

            item_type = item.get("@type")
            if isinstance(item_type, list):
                is_job = any(str(value).lower() == "jobposting" for value in item_type)
            else:
                is_job = str(item_type).lower() == "jobposting"

            if not is_job:
                continue

            parts = []
            for key in ("title", "description", "responsibilities", "qualifications", "skills"):
                value = item.get(key)
                if isinstance(value, str) and value.strip():
                    parts.append(value.strip())

            hiring_org = item.get("hiringOrganization")
            if isinstance(hiring_org, dict):
                org_name = hiring_org.get("name")
                if isinstance(org_name, str) and org_name.strip():
                    parts.insert(0, org_name.strip())

            result = _clean_text("\n".join(parts))
            if len(result) > 200:
                return result

    return ""


def _extract_visible_job_text(soup: BeautifulSoup) -> str:
    for tag_name in ("script", "style", "noscript", "svg", "path", "footer", "header", "nav"):
        for tag in soup.find_all(tag_name):
            tag.decompose()

    candidates = []
    selectors = (
        "article",
        "main",
        '[role="main"]',
        '[class*="job"]',
        '[class*="role"]',
        '[class*="description"]',
        '[class*="description"] section',
    )
    for selector in selectors:
        for element in soup.select(selector):
            # Join with a newline, NOT a space. get_text(" ", ...) collapses the whole
            # element into one continuous blob with no real line breaks, which means the
            # per-line noise filter below ends up checking the ENTIRE page's text at
            # once — a single stray "cookie" or "privacy" anywhere on the page then
            # discards everything, not just that line.
            text = _clean_text_preserve_lines(element.get_text("\n", strip=True))
            if len(text) > 200:
                candidates.append(text)

    if not candidates:
        candidates.append(_clean_text_preserve_lines(soup.get_text("\n", strip=True)))

    text = max(candidates, key=len)

    # Remove obvious boilerplate that often dominates careers pages.
    noise_terms = (
        "cookie",
        "privacy",
        "terms",
        "accessibility",
        "consent",
        "sign up for job alerts",
        "follow us",
        "equal opportunity",
        "all rights reserved",
        "manage cookies",
        "newsletter",
        "apply now",
    )

    # Generic nav/chrome labels that are short AND carry no job content — safe to drop
    # outright. Everything else short is kept; real postings are full of short, useful
    # lines ("Python", "3+ years", "Remote", "B.Tech in CS") that a blanket length
    # cutoff would otherwise strip.
    NAV_CHROME = {
        "home", "about", "about us", "contact", "contact us", "login", "log in",
        "sign in", "sign up", "search", "menu", "careers", "back to search results",
        "share", "print", "save job", "saved", "skip to content", "skip to main content",
    }

    lines = []
    seen = set()
    for chunk in re.split(r"(?:\n|\u2022|\|)", text):
        line = _clean_text(chunk)
        if not line or len(line) < 3:
            continue

        lower = line.lower()
        if lower in NAV_CHROME:
            continue
        if any(re.search(rf"\b{re.escape(term)}\b", lower) for term in noise_terms):
            continue

        if lower not in seen:
            seen.add(lower)
            lines.append(line)

    return "\n".join(lines)


def scrape_with_firecrawl(url: str) -> str:
    """
    Optional fast path when FIRECRAWL_API_KEY is available.
    Falls back to HTTP scraping if the Firecrawl client is unavailable or fails.
    """
    api_key = _get_config_value("FIRECRAWL_API_KEY")
    if not api_key:
        return ""

    try:
        from firecrawl import FirecrawlApp

        app = FirecrawlApp(api_key=api_key)
        result = app.scrape_url(url, params={"formats": ["markdown", "html", "text"]})

        for key in ("markdown", "text", "html"):
            value = result.get(key) if isinstance(result, dict) else None
            if isinstance(value, str) and len(value.strip()) > 200:
                return _clean_text(value)
    except Exception:
        return ""

    return ""


def scrape_with_httpx(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/126.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    with httpx.Client(follow_redirects=True, timeout=20.0, headers=headers) as client:
        response = client.get(url)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    title = _clean_text(soup.title.get_text()) if soup.title and soup.title.get_text() else ""
    structured = _extract_jobposting_jsonld(soup)
    visible = _extract_visible_job_text(soup)

    # Prefer structured data, then visible job content, then title as a last resort.
    text = structured or visible

    combined = "\n\n".join(part for part in [title, text] if part)
    return combined


def fetch_jd_from_url(url: str) -> str:
    if _get_config_value("FIRECRAWL_API_KEY"):
        try:
            text = scrape_with_firecrawl(url)
            if text and len(text) > 200:
                return text
        except Exception:
            pass  # Fall through to httpx

    return scrape_with_httpx(url)