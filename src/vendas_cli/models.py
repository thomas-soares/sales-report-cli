from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class Sale:
    date: date | None
    product: str
    quantity: int
    unit_price: Decimal

    @property
    def total(self) -> Decimal:
        return self.quantity * self.unit_price


@dataclass(frozen=True)
class SalesReport:
    totals_by_product: dict[str, Decimal]
    grand_total: Decimal
    best_selling_product: str | None
    start_date: date | None = None
    end_date: date | None = None
