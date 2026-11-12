import json
from pathlib import Path
import subprocess
import sys

import pytest

from vendas_cli.cli import main


def write_sales_csv(path: Path, with_dates: bool = True) -> Path:
    if with_dates:
        content = (
            "data,produto,quantidade,preco_unitario\n"
            "2025-01-01,Camiseta,3,49.90\n"
            "2025-01-31,Tênis,1,199.90\n"
            "2025-02-01,Calça,2,99.90\n"
        )
    else:
        content = (
            "produto,quantidade,preco_unitario\n"
            "Camiseta,3,49.90\n"
            "Tênis,1,199.90\n"
        )
    path.write_text(content, encoding="utf-8")
    return path


def test_main_prints_text_report_to_stdout_and_logs_to_stderr(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = write_sales_csv(tmp_path / "sales.csv")

    result = main([str(path)])

    captured = capsys.readouterr()
    assert result == 0
    assert "Product" in captured.out
    assert "Camiseta" in captured.out
    assert "Grand total:" in captured.out
    assert "CSV parsing complete" in captured.err
    assert "CSV parsing complete" not in captured.out


def test_main_prints_json_report(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = write_sales_csv(tmp_path / "sales.csv")

    result = main([str(path), "--format", "json"])

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert result == 0
    assert data["totals_by_product"]["Camiseta"] == 149.7
    assert data["period"] == {"start": None, "end": None}


def test_command_writes_utf8_json_to_stdout(tmp_path: Path) -> None:
    path = write_sales_csv(tmp_path / "sales.csv")

    result = subprocess.run(
        [sys.executable, "-m", "vendas_cli.cli", str(path), "--format", "json"],
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    data = json.loads(result.stdout.decode("utf-8"))
    assert set(data["totals_by_product"]) == {"Camiseta", "Tênis", "Calça"}


def test_main_applies_inclusive_date_bounds(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = write_sales_csv(tmp_path / "sales.csv")

    result = main(
        [
            str(path),
            "--start",
            "2025-01-01",
            "--end",
            "2025-01-31",
            "--format",
            "json",
        ]
    )

    data = json.loads(capsys.readouterr().out)
    assert result == 0
    assert set(data["totals_by_product"]) == {"Camiseta", "Tênis"}
    assert data["period"] == {"start": "2025-01-01", "end": "2025-01-31"}


@pytest.mark.parametrize(
    ("arguments", "expected_error", "expected_code"),
    [
        (["missing.csv"], "No such file or directory", 1),
        ([], "the following arguments are required", 2),
    ],
)
def test_main_returns_expected_error_code_without_traceback(
    arguments: list[str],
    expected_error: str,
    expected_code: int,
    capsys: pytest.CaptureFixture[str],
) -> None:
    result = main(arguments)

    captured = capsys.readouterr()
    assert result == expected_code
    assert expected_error.lower() in (captured.err + captured.out).lower()
    assert "Traceback" not in captured.err


def test_main_rejects_date_filter_without_date_column(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = write_sales_csv(tmp_path / "sales.csv", with_dates=False)

    result = main([str(path), "--start", "2025-01-01"])

    captured = capsys.readouterr()
    assert result == 1
    assert "date column" in captured.err.lower()
    assert captured.out == ""
    assert "Traceback" not in captured.err


@pytest.mark.parametrize(
    "arguments",
    [
        ["sales.csv", "--start", "not-a-date"],
        ["sales.csv", "--format", "xml"],
        ["sales.csv", "--start", "2025-02-01", "--end", "2025-01-01"],
    ],
)
def test_main_returns_usage_error_for_invalid_arguments(
    arguments: list[str], capsys: pytest.CaptureFixture[str]
) -> None:
    result = main(arguments)

    captured = capsys.readouterr()
    assert result == 2
    assert "usage:" in captured.err.lower()
    assert "Traceback" not in captured.err


def test_main_returns_data_error_for_invalid_csv(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "invalid.csv"
    path.write_text("wrong,headers\nvalue,value\n", encoding="utf-8")

    result = main([str(path)])

    captured = capsys.readouterr()
    assert result == 1
    assert "required columns" in captured.err.lower()
    assert captured.out == ""
    assert "Traceback" not in captured.err


@pytest.mark.parametrize("arguments", [["--help"], ["--version"]])
def test_main_returns_success_for_help_and_version(
    arguments: list[str], capsys: pytest.CaptureFixture[str]
) -> None:
    result = main(arguments)

    captured = capsys.readouterr()
    assert result == 0
    assert "vendas-cli" in captured.out


def test_verbose_flag_enables_debug_logging(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = write_sales_csv(tmp_path / "sales.csv")

    result = main([str(path), "--verbose"])
    error_output = capsys.readouterr().err

    assert result == 0
    assert "DEBUG" in error_output
    assert "Reading CSV file" in error_output
