from __future__ import annotations

from bs4 import BeautifulSoup

from ..models import Listing
from .base import ScraperError, get, parse_es_price

STORE = "Amazon.es"
BASE = "https://www.amazon.es"
URL = BASE + "/s?k=rtx+5090"


def parse(html: str) -> list[Listing]:
    soup = BeautifulSoup(html, "lxml")
    out: list[Listing] = []
    for res in soup.select('div[data-component-type="s-search-result"]'):
        asin = res.get("data-asin")
        title = res.select_one("h2")
        if not asin or not title:
            continue
        price_el = res.select_one("span.a-price > span.a-offscreen")
        price = parse_es_price(price_el.get_text()) if price_el else None
        out.append(
            Listing(STORE, title.get_text(" ", strip=True), price, price is not None, f"{BASE}/dp/{asin}")
        )
    return out


def fetch() -> list[Listing]:
    html = get(URL).text
    if "captcha" in html.lower() and "s-search-result" not in html:
        raise ScraperError("Amazon: captcha")
    listings = parse(html)
    if not listings:
        raise ScraperError("Amazon: sin productos (¿cambió el HTML?)")
    return listings
