from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Listing:
    store: str
    title: str
    price: float | None  # EUR; None si no hay precio visible
    in_stock: bool
    url: str
