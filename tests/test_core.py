from datetime import datetime, timezone

from gpu import db, report
from gpu.models import Listing
from gpu.stats import compute, deals


def L(price, stock=True, store="X"):
    return Listing(store, "RTX 5090 test", price, stock, "https://e.x/1")


def test_stats_only_in_stock():
    s = compute([L(2000), L(3000), L(100, stock=False), L(None)])
    assert (s.count, s.mean, s.median, s.min) == (2, 2500.0, 2500.0, 2000.0)
    assert compute([L(1, stock=False)]).mean is None


def test_deals_sorted():
    d = deals([L(2400), L(2100), L(2600), L(1000, stock=False)], 2500)
    assert [x.price for x in d] == [2100, 2400]


def test_db_and_report(tmp_path):
    con = db.connect(tmp_path / "t.db")
    db.save_run(con, [L(9000)], datetime(2026, 1, 1, tzinfo=timezone.utc))
    db.save_run(con, [L(8000), L(2400, store="<b>")], datetime(2026, 1, 2, tzinfo=timezone.utc))
    assert len(db.load_runs(con)) == 2
    out = report.build(con, 2500, tmp_path / "r.html")
    page = out.read_text(encoding="utf8")
    assert "1 oferta(s) por debajo" in page
    assert "&lt;b&gt;" in page and "<b>" not in page.split('<table>')[1].split("</table>")[0]
