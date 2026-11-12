from dataclasses import FrozenInstanceError
from datetime import date
from decimal import Decimal

import pytest

from vendas_cli.models import Sale, SalesReport


def test_sale_total_uses_decimal_arithmetic() -> None:
    sale = Sale(
        date=date(2026, 1, 2),
        product="Notebook",
        quantity=2,
        unit_price=Decimal("3500.00"),
    )

    assert sale.total == Decimal("7000.00")


def test_sale_date_can_be_missing() -> None:
    sale = Sale(
        date=None,
        product="Mouse",
        quantity=3,
        unit_price=Decimal("75.90"),
    )

    assert sale.date is None
    assert sale.total == Decimal("227.70")


def test_sale_is_frozen() -> None:
    sale = Sale(
        date=None,
        product="Mouse",
        quantity=1,
        unit_price=Decimal("10.00"),
    )

    with pytest.raises(FrozenInstanceError):
        sale.quantity = 2


def test_sales_report_stores_totals_and_optional_period() -> None:
    report = SalesReport(
        totals_by_product={"Notebook": Decimal("7000.00")},
        quantity_by_product={"Notebook": 2},
        grand_total=Decimal("7000.00"),
        best_selling_product="Notebook",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
    )

    assert report.totals_by_product == {"Notebook": Decimal("7000.00")}
    assert report.quantity_by_product == {"Notebook": 2}
    assert report.grand_total == Decimal("7000.00")
    assert report.best_selling_product == "Notebook"
    assert report.start_date == date(2026, 1, 1)
    assert report.end_date == date(2026, 1, 31)


def test_sales_report_defaults_to_no_product_or_period() -> None:
    report = SalesReport(
        totals_by_product={},
        quantity_by_product={},
        grand_total=Decimal("0.00"),
        best_selling_product=None,
    )

    assert report.best_selling_product is None
    assert report.start_date is None
    assert report.end_date is None
