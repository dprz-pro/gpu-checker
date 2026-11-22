from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_STORES = {"ldlc": True, "alternate": True, "amazon": True, "nvidia_fe": True}


@dataclass
class Config:
    target_price: float = 2500
    min_price: float = 1000
    max_price: float = 20000
    stores: dict[str, bool] = field(default_factory=lambda: dict(DEFAULT_STORES))


def load_config(path: str | Path = "config.toml") -> Config:
    p = Path(path)
    cfg = Config()
    if not p.exists():
        return cfg
    data = tomllib.loads(p.read_text(encoding="utf8"))
    for key in ("target_price", "min_price", "max_price"):
        if key in data:
            setattr(cfg, key, float(data[key]))
    cfg.stores.update({k: bool(v) for k, v in data.get("stores", {}).items()})
    return cfg
