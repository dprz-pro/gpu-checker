from __future__ import annotations

import html
import json
from pathlib import Path

from .db import load_runs
from .stats import compute, deals

TEMPLATE = """<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>RTX 5090 Tracker</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
:root{--bg:#fff;--fg:#1a1a1a;--mut:#666;--line:#ddd;--ok:#0a7d33;--okbg:#e6f6ec}
@media(prefers-color-scheme:dark){:root{--bg:#111;--fg:#eee;--mut:#999;--line:#333;--ok:#4ade80;--okbg:#10301c}}
body{font-family:system-ui,sans-serif;background:var(--bg);color:var(--fg);max-width:1000px;margin:0 auto;padding:16px}
h1{font-size:1.4rem}.banner{padding:12px 16px;border-radius:8px;margin:12px 0;border:1px solid var(--line)}
.banner.ok{background:var(--okbg);border-color:var(--ok);color:var(--ok);font-weight:600}
.cards{display:flex;gap:12px;flex-wrap:wrap}.card{flex:1;min-width:140px;border:1px solid var(--line);border-radius:8px;padding:10px}
.card b{display:block;font-size:1.3rem}.card span{color:var(--mut);font-size:.8rem}
table{width:100%;border-collapse:collapse;margin-top:12px;font-size:.9rem}
th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line)}tr.deal td{background:var(--okbg)}
a{color:inherit}.mut{color:var(--mut)}.wrap{overflow-x:auto}
</style></head><body>
<h1>RTX 5090 · España</h1>
<p class="mut">Última comprobación: __TS__ · Objetivo: __TARGET__ €</p>
__BANNER__
<div class="cards">__CARDS__</div>
<h2>Evolución (solo ofertas en stock)</h2>
<canvas id="c" height="110"></canvas>
<h2>Ofertas actuales</h2>
<div class="wrap"><table><tr><th>Tienda</th><th>Producto</th><th>Precio</th><th>Stock</th></tr>__ROWS__</table></div>
<script>
const D=__DATA__;
const css=getComputedStyle(document.documentElement);
new Chart(document.getElementById('c'),{type:'line',data:{labels:D.labels,datasets:[
{label:'Media',data:D.mean,borderColor:'#3b82f6',tension:.2,spanGaps:true},
{label:'Mediana',data:D.median,borderColor:'#f59e0b',tension:.2,spanGaps:true},
{label:'Mínimo',data:D.min,borderColor:'#10b981',tension:.2,spanGaps:true},
{label:'Objetivo',data:D.labels.map(()=>D.target),borderColor:'#ef4444',borderDash:[6,4],pointRadius:0}]},
options:{scales:{y:{ticks:{callback:v=>v.toLocaleString('es-ES')+' €'}}},
plugins:{tooltip:{callbacks:{label:c=>c.dataset.label+': '+(c.parsed.y??0).toLocaleString('es-ES')+' €'}}}}});
</script></body></html>"""


def _eur(v: float | None) -> str:
    return "—" if v is None else f"{v:,.0f} €".replace(",", ".")


def build(con, target: float, out: str | Path = "report.html") -> Path:
    runs = load_runs(con)
    if not runs:
        raise SystemExit("Aún no hay datos. Ejecuta `gpu check` primero.")
    series = [(ts, compute(ls)) for _, ts, ls in runs]
    data = {
        "labels": [ts.replace("T", " ")[:16] for ts, _ in series],
        "mean": [s.mean for _, s in series],
        "median": [s.median for _, s in series],
        "min": [s.min for _, s in series],
        "target": target,
    }
    ts, listings = runs[-1][1], runs[-1][2]
    cur = compute(listings)
    found = deals(listings, target)
    banner = (
        f'<div class="banner ok">¡{len(found)} oferta(s) por debajo de {_eur(target)}! '
        f'La mejor: {_eur(found[0].price)} en {html.escape(found[0].store)}</div>'
        if found
        else f'<div class="banner">Ninguna oferta en stock por debajo de {_eur(target)}.</div>'
    )
    cards = "".join(
        f'<div class="card"><b>{v}</b><span>{k}</span></div>'
        for k, v in [("Media", _eur(cur.mean)), ("Mediana", _eur(cur.median)),
                     ("Mínimo", _eur(cur.min)), ("En stock", str(cur.count))]
    )
    rows = "".join(
        f'<tr class="{"deal" if l in found else ""}"><td>{html.escape(l.store)}</td>'
        f'<td><a href="{html.escape(l.url)}" target="_blank" rel="noopener">{html.escape(l.title)}</a></td>'
        f'<td>{_eur(l.price)}</td><td>{"Sí" if l.in_stock else "No"}</td></tr>'
        for l in sorted(listings, key=lambda l: (not l.in_stock, l.price or 1e12))
    )
    page = (TEMPLATE.replace("__TS__", html.escape(ts)).replace("__TARGET__", f"{target:,.0f}".replace(",", "."))
            .replace("__BANNER__", banner).replace("__CARDS__", cards).replace("__ROWS__", rows)
            .replace("__DATA__", json.dumps(data).replace("</", "<\\/")))
    out = Path(out)
    out.write_text(page, encoding="utf8")
    return out
