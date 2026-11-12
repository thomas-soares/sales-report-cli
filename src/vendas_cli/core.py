from collections.abc import Iterable, Sequence
from datetime import date
from decimal import Decimal

from .models import Sale, SalesReport


def filter_by_date(
    sales: Sequence[Sale],
    start: date | None = None,
    end: date | None = None,
) -> list[Sale]:
    if start is None and end is None:
        return list(sales)

    return [
        sale
        for sale in sales
        if sale.date is not None
        and (start is None or sale.date >= start)
        and (end is None or sale.date <= end)
    ]


def total_by_product(sales: Iterable[Sale]) -> dict[str, Decimal]:
    totals: dict[str, Decimal] = {}
    for sale in sales:
        totals[sale.product] = totals.get(sale.product, Decimal("0")) + sale.total
    return totals


def quantity_by_product(sales: Iterable[Sale]) -> dict[str, int]:
    quantities: dict[str, int] = {}
    for sale in sales:
        quantities[sale.product] = quantities.get(sale.product, 0) + sale.quantity
    return quantities


def grand_total(sales: Iterable[Sale]) -> Decimal:
    return sum((sale.total for sale in sales), Decimal("0"))


def best_selling_product(sales: Iterable[Sale]) -> str | None:
    quantities: dict[str, int] = {}
    totals: dict[str, Decimal] = {}
    for sale in sales:
        quantities[sale.product] = quantities.get(sale.product, 0) + sale.quantity
        totals[sale.product] = totals.get(sale.product, Decimal("0")) + sale.total

    if not quantities:
        return None

    return min(
        quantities,
        key=lambda product: (-quantities[product], -totals[product], product),
    )


def generate_report(
    sales: Sequence[Sale],
    start: date | None = None,
    end: date | None = None,
) -> SalesReport:
    filtered_sales = filter_by_date(sales, start, end)
    return SalesReport(
        totals_by_product=total_by_product(filtered_sales),
        quantity_by_product=quantity_by_product(filtered_sales),
        grand_total=grand_total(filtered_sales),
        best_selling_product=best_selling_product(filtered_sales),
        start_date=start,
        end_date=end,
    )
