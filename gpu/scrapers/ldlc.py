from __future__ import annotations

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from ..models import Listing
from .base import ScraperError, get

STORE = "LDLC"
BASE = "https://www.ldlc.com"
URL = BASE + "/es-es/buscar/rtx+5090/"


def parse(html: str) -> list[Listing]:
    soup = BeautifulSoup(html, "lxml")
    out: list[Listing] = []
    for item in soup.select("li.pdt-item"):
        link = item.select_one("h3 a")
        if not link:
            continue
        price = None
        box = item.select_one("div.price div.price")
        if box:
            sup = box.find("sup")
            cents = sup.get_text(strip=True) if sup else "00"
            if sup:
                sup.extract()
            digits = re.sub(r"\D", "", box.get_text())
            if digits:
                price = float(f"{digits}.{cents}")
        stock = item.select_one("div.stock")
        in_stock = bool(stock and stock.get_text(strip=True).lower().startswith("en stock"))
        out.append(
            Listing(STORE, link.get_text(strip=True), price, in_stock, urljoin(BASE, link["href"]))
        )
    return out


def fetch() -> list[Listing]:
    listings = parse(get(URL).text)
    if not listings:
        raise ScraperError("LDLC: sin productos (¿cambió el HTML?)")
    return listings
