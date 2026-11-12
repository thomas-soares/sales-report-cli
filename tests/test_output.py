import json
from datetime import date
from decimal import Decimal

import pytest

from vendas_cli.models import SalesReport
from vendas_cli.output import render


def make_report() -> SalesReport:
    return SalesReport(
        totals_by_product={"Camiseta": Decimal("149.70"), "Tênis": Decimal("199.90")},
        quantity_by_product={"Camiseta": 4, "Tênis": 1},
        grand_total=Decimal("349.60"),
        best_selling_product="Camiseta",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 31),
    )


def test_renders_aligned_text_table_with_summary() -> None:
    text = render(make_report(), "text")

    assert "Product" in text
    assert "Quantity" in text
    assert "Total" in text
    assert "Camiseta" in text
    assert "Tênis" in text
    assert "349.60" in text
    assert "Best-selling product: Camiseta" in text
    assert "2025-01-01" in text
    assert "2025-01-31" in text


def test_renders_json_with_numeric_two_decimal_money_and_unicode() -> None:
    rendered = render(make_report(), "json")
    data = json.loads(rendered)

    assert data["totals_by_product"] == {"Camiseta": 149.7, "Tênis": 199.9}
    assert data["quantity_by_product"] == {"Camiseta": 4, "Tênis": 1}
    assert data["grand_total"] == 349.6
    assert data["best_selling_product"] == "Camiseta"
    assert data["period"] == {"start": "2025-01-01", "end": "2025-01-31"}
    assert '"Camiseta": 149.70' in rendered
    assert '"Tênis": 199.90' in rendered
    assert '"grand_total": 349.60' in rendered
    assert "\\u00e9" not in rendered


def test_renders_empty_report() -> None:
    report = SalesReport({}, {}, Decimal("0.00"), None)

    text = render(report)
    data = json.loads(render(report, "json"))

    assert "0.00" in text
    assert data["best_selling_product"] is None
    assert data["totals_by_product"] == {}
    assert data["period"] == {"start": None, "end": None}


def test_rejects_unknown_format() -> None:
    with pytest.raises(ValueError, match="format"):
        render(make_report(), "xml")
