import json
from collections.abc import Callable, Mapping
from decimal import Decimal
from typing import TypeVar

from .models import SalesReport

T = TypeVar("T")


def _format_money(value: Decimal) -> str:
    return f"{value.quantize(Decimal('0.01')):.2f}"


def _format_quantity(value: int) -> str:
    return str(value)


def _format_text(report: SalesReport) -> str:
    products = sorted(set(report.totals_by_product) | set(report.quantity_by_product))
    rows = [
        (
            product,
            str(report.quantity_by_product.get(product, 0)),
            _format_money(report.totals_by_product.get(product, Decimal("0"))),
        )
        for product in products
    ]
    headers = ("Product", "Quantity", "Total")
    widths = tuple(
        max([len(header), *(len(row[index]) for row in rows)])
        for index, header in enumerate(headers)
    )

    lines = [
        f"{headers[0]:<{widths[0]}} | "
        f"{headers[1]:>{widths[1]}} | "
        f"{headers[2]:>{widths[2]}}",
        f"{'-' * widths[0]}-+-{'-' * widths[1]}-+-{'-' * widths[2]}",
    ]
    lines.extend(
        f"{product:<{widths[0]}} | "
        f"{quantity:>{widths[1]}} | "
        f"{total:>{widths[2]}}"
        for product, quantity, total in rows
    )
    lines.append(f"Grand total: {_format_money(report.grand_total)}")
    lines.append(
        f"Best-selling product: {report.best_selling_product or 'None'}"
    )

    if report.start_date is not None and report.end_date is not None:
        lines.append(
            f"Period: {report.start_date.isoformat()} to {report.end_date.isoformat()}"
        )
    elif report.start_date is not None:
        lines.append(f"Period: from {report.start_date.isoformat()}")
    elif report.end_date is not None:
        lines.append(f"Period: through {report.end_date.isoformat()}")

    return "\n".join(lines)


def _json_mapping_lines(
    name: str,
    values: Mapping[str, T],
    format_value: Callable[[T], str],
) -> list[str]:
    lines = [f'  "{name}": {{']
    ordered_products = sorted(values)
    for index, product in enumerate(ordered_products):
        formatted_value = format_value(values[product])
        comma = "," if index < len(ordered_products) - 1 else ""
        encoded_product = json.dumps(product, ensure_ascii=False)
        lines.append(f"    {encoded_product}: {formatted_value}{comma}")
    lines.append("  },")
    return lines


def _format_json(report: SalesReport) -> str:
    start = (
        json.dumps(report.start_date.isoformat(), ensure_ascii=False)
        if report.start_date is not None
        else "null"
    )
    end = (
        json.dumps(report.end_date.isoformat(), ensure_ascii=False)
        if report.end_date is not None
        else "null"
    )
    best_selling_product = (
        json.dumps(report.best_selling_product, ensure_ascii=False)
        if report.best_selling_product is not None
        else "null"
    )

    lines = ["{"]
    lines.extend(_json_mapping_lines(
        "totals_by_product", report.totals_by_product, _format_money
    ))
    lines.extend(
        _json_mapping_lines(
            "quantity_by_product", report.quantity_by_product, _format_quantity
        )
    )
    lines.append(f'  "grand_total": {_format_money(report.grand_total)},')
    lines.append(f'  "best_selling_product": {best_selling_product},')
    lines.append('  "period": {')
    lines.append(f'    "start": {start},')
    lines.append(f'    "end": {end}')
    lines.append("  }")
    lines.append("}")
    return "\n".join(lines)


def render(report: SalesReport, format: str = "text") -> str:
    if format == "text":
        return _format_text(report)
    if format == "json":
        return _format_json(report)
    raise ValueError(f"Unsupported output format: {format}.")
