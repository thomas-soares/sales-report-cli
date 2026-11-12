import csv
import io
import logging
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .models import Sale

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = ("produto", "quantidade", "preco_unitario")
DATE_COLUMNS = ("data", "data_venda", "date")


class CSVFormatError(ValueError):
    """Raised when a CSV file is empty or has an invalid header."""


@dataclass(frozen=True)
class CSVParseResult:
    sales: list[Sale]
    has_date_column: bool
    rows_read: int
    rows_skipped: int


def parse_sales_csv(path: str | Path) -> CSVParseResult:
    csv_path = Path(path)
    raw_data = csv_path.read_bytes()

    try:
        content = raw_data.decode("utf-8-sig")
    except UnicodeDecodeError:
        content = raw_data.decode("latin-1")

    reader = csv.DictReader(io.StringIO(content, newline=""))
    if not reader.fieldnames:
        raise CSVFormatError("CSV file is empty or has no header.")

    columns = {
        header.strip().casefold(): header
        for header in reader.fieldnames
        if header is not None
    }
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in columns]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise CSVFormatError(f"CSV file is missing required columns: {missing}.")

    date_column = next((columns[name] for name in DATE_COLUMNS if name in columns), None)
    if date_column is None:
        logger.info("CSV has no date column; date filter is unavailable.")

    sales: list[Sale] = []
    rows_read = 0
    rows_skipped = 0
    for row in reader:
        line_number = reader.line_num
        rows_read += 1
        try:
            if None in row:
                raise ValueError("row contains more values than the header")

            product_value = row[columns["produto"]]
            quantity_value = row[columns["quantidade"]]
            unit_price_value = row[columns["preco_unitario"]]
            if not isinstance(product_value, str):
                raise ValueError("product is missing")
            if not isinstance(quantity_value, str):
                raise ValueError("quantity is missing")
            if not isinstance(unit_price_value, str):
                raise ValueError("unit price is missing")

            product = product_value.strip()
            if not product:
                raise ValueError("product is empty")

            quantity = int(quantity_value.strip())
            unit_price = Decimal(unit_price_value.strip())
            if not unit_price.is_finite():
                raise ValueError("unit price must be a finite number")

            sale_date: date | None = None
            if date_column is not None:
                date_value = row[date_column]
                if date_value is not None:
                    if not isinstance(date_value, str):
                        raise ValueError("date must contain a single value")
                    date_text = date_value.strip()
                    if date_text:
                        sale_date = date.fromisoformat(date_text)
                        if sale_date.isoformat() != date_text:
                            raise ValueError("date must use YYYY-MM-DD format")

            sales.append(
                Sale(
                    date=sale_date,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                )
            )
        except (InvalidOperation, TypeError, ValueError) as error:
            rows_skipped += 1
            logger.warning("Skipping invalid CSV row at line %d: %s", line_number, error)

    logger.info(
        "CSV parsing complete: %d rows read, %d valid, %d skipped.",
        rows_read,
        len(sales),
        rows_skipped,
    )
    return CSVParseResult(
        sales=sales,
        has_date_column=date_column is not None,
        rows_read=rows_read,
        rows_skipped=rows_skipped,
    )
