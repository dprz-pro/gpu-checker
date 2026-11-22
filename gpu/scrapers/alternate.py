from __future__ import annotations

from urllib.parse import urljoin

from bs4 import BeautifulSoup

from ..models import Listing
from .base import ScraperError, get, parse_es_price

STORE = "Alternate"
BASE = "https://www.alternate.es"
URL = BASE + "/listing.xhtml?q=rtx+5090"


def parse(html: str) -> list[Listing]:
    soup = BeautifulSoup(html, "lxml")
    out: list[Listing] = []
    for card in soup.select("a.productBox"):
        name = card.select_one(".product-name")
        if not name:
            continue
        price_el = card.select_one("span.price")
        price = parse_es_price(price_el.get_text()) if price_el else None
        avail = card.select_one(".delivery-info")
        in_stock = bool(avail and avail.get_text(strip=True).lower().startswith("en stock"))
        out.append(
            Listing(STORE, name.get_text(" ", strip=True), price, in_stock, urljoin(BASE, card["href"]))
        )
    return out


MAX_PAGES = 4


def fetch(get_page=get) -> list[Listing]:
    """Recorre páginas hasta que una no aporte ninguna 5090 nueva."""
    listings: list[Listing] = []
    seen: set[str] = set()
    for page in range(1, MAX_PAGES + 1):
        batch = parse(get_page(f"{URL}&page={page}").text)
        new = [l for l in batch if l.url not in seen and "5090" in l.title]
        if not new:
            break
        seen.update(l.url for l in new)
        listings += new
    if not listings:
        raise ScraperError("Alternate: sin productos (¿cambió el HTML?)")
    return listings
