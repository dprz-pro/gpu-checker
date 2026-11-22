from __future__ import annotations

import re

from .models import Listing

# Variantes y productos que NO son una RTX 5090 estándar suelta.
_EXCLUDE = re.compile(
    r"5090\s*d\b|"  # RTX 5090 D (modelo para China)
    r"port[aá]til|laptop|notebook|sobremesa|ordenador|\bpc\b|torre|gaming pc|"
    r"waterblock|water block|bloque|backplate|soporte|cable|adaptador|"
    r"funda|caja|refrigeraci[oó]n l[ií]quida",
    re.IGNORECASE,
)
_IS_5090 = re.compile(r"5090", re.IGNORECASE)


def is_rtx5090_card(title: str) -> bool:
    return bool(_IS_5090.search(title)) and not _EXCLUDE.search(title)


def keep(listing: Listing, min_price: float, max_price: float) -> bool:
    if not is_rtx5090_card(listing.title):
        return False
    if listing.price is None:
        return True  # sin precio: se guarda como no disponible
    return min_price <= listing.price <= max_price
