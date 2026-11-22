"""Founders Edition en el marketplace oficial de Nvidia (España).

AVISO: el formato del API NO está verificado contra datos reales (no pude
consultarlo desde el entorno de desarrollo). El parser es defensivo y si no
encuentra la FE lanza ScraperError en vez de inventar un resultado.
Valida con `gpu check` en tu PC y ajusta `parse()` si hace falta.
"""

from __future__ import annotations

from ..models import Listing
from .base import ScraperError, get

STORE = "Nvidia FE"
PAGE = "https://marketplace.nvidia.com/es-es/consumer/graphics-cards/?locale=es-es&gpu=RTX%205090"
API = "https://api.nvidia.partners/edge/product/search"
PARAMS = {"page": 1, "limit": 12, "locale": "es-es", "gpu": "RTX 5090", "manufacturer": "NVIDIA"}

_OUT = {"out_of_stock", "outofstock", "no_stock", "agotado"}


def _to_price(v) -> float | None:
    try:
        return float(str(v).replace("€", "").replace(",", ".").strip())
    except (TypeError, ValueError):
        return None


def parse(data: dict) -> list[Listing]:
    block = data.get("searchedProducts") or {}
    products = list(block.get("productDetails") or [])
    if block.get("featuredProduct"):
        products.append(block["featuredProduct"])
    out: list[Listing] = []
    for p in products:
        title = p.get("productTitle") or p.get("displayName") or ""
        if "5090" not in title:
            continue
        status = str(p.get("prdStatus", "")).lower().replace(" ", "_")
        out.append(Listing(STORE, title, _to_price(p.get("productPrice")), status not in _OUT and bool(status), PAGE))
    return out


def fetch() -> list[Listing]:
    try:
        data = get(API, params=PARAMS).json()
    except ValueError as e:
        raise ScraperError(f"Nvidia: respuesta no JSON ({e})") from e
    listings = parse(data)
    if not listings:
        raise ScraperError("Nvidia: no se encontró la RTX 5090 FE en la respuesta")
    return listings
