from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, median

from .models import Listing


@dataclass
class Stats:
    count: int
    mean: float | None
    median: float | None
    min: float | None


def compute(listings: list[Listing]) -> Stats:
    """Estadísticas sobre ofertas EN STOCK con precio."""
    prices = [l.price for l in listings if l.in_stock and l.price is not None]
    if not prices:
        return Stats(0, None, None, None)
    return Stats(len(prices), round(mean(prices), 2), round(median(prices), 2), min(prices))


def deals(listings: list[Listing], target: float) -> list[Listing]:
    return sorted(
        (l for l in listings if l.in_stock and l.price is not None and l.price <= target),
        key=lambda l: l.price,
    )
