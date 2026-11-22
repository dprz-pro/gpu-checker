from pathlib import Path

from gpu.filters import is_rtx5090_card, keep
from gpu.scrapers import alternate, amazon, ldlc
from gpu.scrapers.base import parse_es_price

FX = Path(__file__).parent / "fixtures"


def test_parse_es_price():
    assert parse_es_price("€ 10.168,00") == 10168.0
    assert parse_es_price("9.968,23 €") == 9968.23
    assert parse_es_price("sin precio") is None


def test_ldlc():
    items = ldlc.parse((FX / "ldlc.html").read_text(encoding="utf8"))
    assert len(items) == 16
    first = items[0]
    assert first.title == "Gainward GeForce RTX 5090 Phantom"
    assert first.price == 9211.95 and first.in_stock
    assert first.url.startswith("https://www.ldlc.com/es-es/ficha/")
    assert not next(i for i in items if "TUF" in i.title).in_stock  # Agotado
    assert not next(i for i in items if "SUPRIM" in i.title).in_stock  # En 7 días


def test_alternate():
    items = alternate.parse((FX / "alternate.html").read_text(encoding="utf8"))
    assert len(items) == 24
    astral = items[0]
    assert "ROG ASTRAL" in astral.title and astral.price == 10168.0 and astral.in_stock


def test_amazon_and_filter():
    items = amazon.parse((FX / "amazon.html").read_text(encoding="utf8"))
    assert items
    kept = [i for i in items if keep(i, 1000, 20000)]
    assert kept and all("5090" in i.title for i in kept)
    assert not any("sobremesa" in i.title.lower() for i in kept)  # PC completo fuera


def test_filter_rules():
    assert is_rtx5090_card("MSI GeForce RTX 5090 32G VENTUS 3X OC")
    assert not is_rtx5090_card("Gigabyte RTX 5090 D 32G")
    assert not is_rtx5090_card("Portátil MSI Titan con RTX 5090")
    assert not is_rtx5090_card("Waterblock para RTX 5090")
    assert not is_rtx5090_card("MSI RTX 5080 16G")


def test_alternate_pagination_stops_when_no_new_items():
    html = (FX / "alternate.html").read_text(encoding="utf8")
    calls = []

    class R:
        text = html

    def fake_get(url):
        calls.append(url)
        return R()

    items = alternate.fetch(fake_get)
    assert len(calls) == 2  # la 2ª página repite los mismos productos -> corta
    assert len({i.url for i in items}) == len(items)
