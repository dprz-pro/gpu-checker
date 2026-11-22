from __future__ import annotations

import argparse

from . import db, report
from .config import load_config
from .filters import keep
from .scrapers import SCRAPERS
from .scrapers.base import ScraperError
from .stats import compute, deals


def _eur(v):
    return "—" if v is None else f"{v:,.0f} €".replace(",", ".")


def cmd_check(args) -> None:
    cfg = load_config(args.config)
    listings = []
    for name, module in SCRAPERS.items():
        if not cfg.stores.get(name):
            continue
        try:
            found = [l for l in module.fetch() if keep(l, cfg.min_price, cfg.max_price)]
        except (ScraperError, Exception) as e:  # una tienda caída no tumba el resto
            print(f"  ✗ {name}: {e}")
            continue
        print(f"  ✓ {name}: {len(found)} productos")
        listings += found
    if not listings:
        raise SystemExit("Ninguna tienda devolvió datos; no se guarda nada.")
    con = db.connect(args.db)
    db.save_run(con, listings)
    s = compute(listings)
    print(f"\nEn stock: {s.count} · media {_eur(s.mean)} · mediana {_eur(s.median)} · mínimo {_eur(s.min)}")
    found = deals(listings, cfg.target_price)
    if found:
        print(f"\n🔔 ¡{len(found)} oferta(s) por debajo de {_eur(cfg.target_price)}!")
        for l in found:
            print(f"   {_eur(l.price)}  {l.store}  {l.title}\n   {l.url}")
    else:
        print(f"\nNada en stock por debajo de {_eur(cfg.target_price)}.")
    out = report.build(con, cfg.target_price, args.out)
    print(f"Informe: {out}")


def cmd_report(args) -> None:
    cfg = load_config(args.config)
    print(f"Informe: {report.build(db.connect(args.db), cfg.target_price, args.out)}")


def main() -> None:
    p = argparse.ArgumentParser(prog="gpu", description="Rastreador RTX 5090 España")
    p.add_argument("--config", default="config.toml")
    p.add_argument("--db", default="data/prices.db")
    p.add_argument("--out", default="report.html")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check", help="consulta las tiendas, guarda y genera el informe").set_defaults(fn=cmd_check)
    sub.add_parser("report", help="regenera el informe con los datos guardados").set_defaults(fn=cmd_report)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
