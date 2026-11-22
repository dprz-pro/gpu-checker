from __future__ import annotations

from . import alternate, amazon, ldlc, nvidia

# nombre en config -> módulo con fetch() -> list[Listing]
SCRAPERS = {
    "ldlc": ldlc,
    "alternate": alternate,
    "amazon": amazon,
    "nvidia_fe": nvidia,
}
