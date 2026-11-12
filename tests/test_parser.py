import logging
from datetime import date
from pathlib import Path

import pytest
from _pytest.logging import LogCaptureFixture

from vendas_cli.parser import CSVFormatError, parse_sales_csv


def test_parses_csv_without_date_column(tmp_path: Path, caplog: LogCaptureFixture) -> None:
    path = tmp_path / "sales.csv"
    path.write_text(
        "produto,quantidade,preco_unitario\r\nCamiseta,3,49.90\r\n",
        encoding="utf-8",
        newline="",
    )

    with caplog.at_level(logging.INFO):
        result = parse_sales_csv(path)

    assert result.has_date_column is False
    assert result.rows_read == 1
    assert result.rows_skipped == 0
    assert result.sales[0].product == "Camiseta"
    assert result.sales[0].date is None
    assert "date filter is unavailable" in caplog.text


@pytest.mark.parametrize("date_header", ["data", "DATA_VENDA", "Date"])
def test_recognizes_date_header_aliases_case_insensitively(
    tmp_path: Path, date_header: str
) -> None:
    path = tmp_path / "sales.csv"
    path.write_text(
        f"{date_header},produto,quantidade,preco_unitario\n"
        "2025-01-02, Camiseta ,3,49.90\n",
        encoding="utf-8",
    )

    result = parse_sales_csv(path)

    assert result.has_date_column is True
    assert result.sales[0].date == date(2025, 1, 2)
    assert result.sales[0].product == "Camiseta"


def test_parses_utf8_bom_and_crlf(tmp_path: Path) -> None:
    path = tmp_path / "sales.csv"
    path.write_bytes(
        "produto,quantidade,preco_unitario\r\nTênis,1,199.90\r\n".encode("utf-8-sig")
    )

    result = parse_sales_csv(path)

    assert result.sales[0].product == "Tênis"


def test_falls_back_to_latin1(tmp_path: Path) -> None:
    path = tmp_path / "sales.csv"
    path.write_bytes(
        "produto,quantidade,preco_unitario\r\nCalça,2,99.90\r\n".encode("latin-1")
    )

    result = parse_sales_csv(path)

    assert result.sales[0].product == "Calça"


def test_repository_sample_preserves_latin1_product_names() -> None:
    sample_path = Path(__file__).parents[1] / "sample" / "vendas.csv"
    dated_sample_path = Path(__file__).parents[1] / "sample" / "vendas-with-date.csv"

    result = parse_sales_csv(sample_path)
    dated_result = parse_sales_csv(dated_sample_path)

    assert [sale.product for sale in result.sales] == [
        "Camiseta",
        "Calça",
        "Camiseta",
        "Tênis",
    ]
    assert [sale.product for sale in dated_result.sales] == [
        "Camiseta",
        "Calça",
        "Camiseta",
        "Tênis",
    ]


def test_blank_date_is_allowed_when_date_column_exists(tmp_path: Path) -> None:
    path = tmp_path / "sales.csv"
    path.write_text(
        "date,produto,quantidade,preco_unitario\n,Camiseta,3,49.90\n",
        encoding="utf-8",
    )

    result = parse_sales_csv(path)

    assert result.has_date_column is True
    assert result.sales[0].date is None


def test_invalid_date_skips_only_the_malformed_row(tmp_path: Path) -> None:
    path = tmp_path / "sales.csv"
    path.write_text(
        "data,produto,quantidade,preco_unitario\n"
        "2025-02-30,Camiseta,3,49.90\n"
        "2025-02-28,Tênis,1,199.90\n",
        encoding="utf-8",
    )

    result = parse_sales_csv(path)

    assert result.rows_read == 2
    assert result.rows_skipped == 1
    assert [sale.product for sale in result.sales] == ["Tênis"]


@pytest.mark.parametrize(
    "content",
    [
        "",
        "produto,quantidade\nCamiseta,3\n",
    ],
)
def test_rejects_empty_file_or_missing_required_headers(
    tmp_path: Path, content: str
) -> None:
    path = tmp_path / "sales.csv"
    path.write_text(content, encoding="utf-8")

    with pytest.raises(CSVFormatError):
        parse_sales_csv(path)


def test_skips_invalid_rows_and_logs_line_number_and_summary(
    tmp_path: Path, caplog: LogCaptureFixture
) -> None:
    path = tmp_path / "sales.csv"
    path.write_text(
        "produto,quantidade,preco_unitario\n"
        "Camiseta,3,49.90\n"
        "Calça,not-an-int,99.90\n",
        encoding="utf-8",
    )

    with caplog.at_level(logging.INFO):
        result = parse_sales_csv(path)

    assert len(result.sales) == 1
    assert result.rows_read == 2
    assert result.rows_skipped == 1
    assert "line 3" in caplog.text
    assert "2 rows read" in caplog.text
    assert "1 skipped" in caplog.text


def test_missing_file_remains_an_explicit_file_error(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        parse_sales_csv(tmp_path / "missing.csv")
