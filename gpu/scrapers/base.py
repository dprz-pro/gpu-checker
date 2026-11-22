from __future__ import annotations

import re

import httpx

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "es-ES,es;q=0.9",
}


class ScraperError(Exception):
    """La tienda bloqueó la petición o cambió su estructura."""


def get(url: str, **kwargs) -> httpx.Response:
    r = httpx.get(url, headers=HEADERS, timeout=30, follow_redirects=True, **kwargs)
    if r.status_code in (403, 429, 503):
        raise ScraperError(f"{url} -> HTTP {r.status_code} (posible anti-bot)")
    r.raise_for_status()
    return r


def parse_es_price(text: str) -> float | None:
    """'10.168,00' / '9.968,23 €' / '€ 10.168,00' -> float."""
    m = re.search(r"\d[\d.\s]*(?:,\d{1,2})?", text)
    if not m:
        return None
    raw = m.group(0).strip().replace(" ", "").replace(".", "").replace(",", ".")
    try:
        return float(raw)
    except ValueError:
        return None
