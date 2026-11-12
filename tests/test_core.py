from datetime import date
from decimal import Decimal

from vendas_cli.core import (
    best_selling_product,
    filter_by_date,
    generate_report,
    grand_total,
    quantity_by_product,
    total_by_product,
)
from vendas_cli.models import Sale


def make_sale(
    sale_date: date | None, product: str, quantity: int, unit_price: str
) -> Sale:
    return Sale(sale_date, product, quantity, Decimal(unit_price))


def test_filter_by_date_includes_both_bounds_and_excludes_undated_sales() -> None:
    sales = [
        make_sale(date(2025, 1, 1), "A", 1, "10.00"),
        make_sale(None, "B", 2, "5.00"),
        make_sale(date(2025, 1, 3), "C", 1, "20.00"),
    ]

    filtered = filter_by_date(sales, date(2025, 1, 1), date(2025, 1, 3))

    assert [sale.product for sale in filtered] == ["A", "C"]


def test_filter_without_bounds_preserves_undated_sales() -> None:
    sales = [make_sale(None, "A", 1, "1.00")]

    assert filter_by_date(sales) == sales


def test_totals_by_product_quantity_and_grand_total_use_decimal() -> None:
    sales = [
        make_sale(None, "A", 2, "10.25"),
        make_sale(None, "A", 1, "2.50"),
        make_sale(None, "B", 1, "5.00"),
    ]

    assert total_by_product(sales) == {"A": Decimal("23.00"), "B": Decimal("5.00")}
    assert quantity_by_product(sales) == {"A": 3, "B": 1}
    assert grand_total(sales) == Decimal("28.00")


def test_best_seller_uses_quantity_then_value_then_name() -> None:
    sales = [
        make_sale(None, "B", 3, "10.00"),
        make_sale(None, "A", 3, "10.00"),
        make_sale(None, "C", 2, "100.00"),
    ]

    assert best_selling_product(sales) == "A"


def test_best_seller_uses_total_value_to_break_quantity_ties() -> None:
    sales = [
        make_sale(None, "A", 2, "10.00"),
        make_sale(None, "B", 2, "11.00"),
    ]

    assert best_selling_product(sales) == "B"


def test_empty_sales_have_zero_total_and_no_best_seller() -> None:
    assert grand_total([]) == Decimal("0")
    assert total_by_product([]) == {}
    assert quantity_by_product([]) == {}
    assert best_selling_product([]) is None


def test_generate_report_uses_filtered_sales_and_keeps_period() -> None:
    sales = [
        make_sale(date(2025, 1, 1), "A", 2, "10.00"),
        make_sale(date(2025, 2, 1), "B", 5, "10.00"),
    ]

    report = generate_report(sales, date(2025, 1, 1), date(2025, 1, 31))

    assert report.totals_by_product == {"A": Decimal("20.00")}
    assert report.quantity_by_product == {"A": 2}
    assert report.grand_total == Decimal("20.00")
    assert report.best_selling_product == "A"
    assert report.start_date == date(2025, 1, 1)
    assert report.end_date == date(2025, 1, 31)
