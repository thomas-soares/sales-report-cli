# Sales Report CLI

A Python command-line tool that reads sales CSV files, calculates totals and best-selling products, applies optional date filters, and renders text or JSON reports.

## Requirements

- Python 3.10 or newer
- `pip`

## Installation

Install the command and its runtime dependencies:

```powershell
python -m pip install .
```

For development, install the test dependencies as well:

```powershell
python -m pip install -e ".[dev]"
```

## Usage

Generate a text report:

```powershell
vendas-cli sample/vendas.csv
```

Generate JSON for a date range (the date interval includes both bounds):

```powershell
vendas-cli sample/vendas-with-date.csv --format json --start 2025-01-01 --end 2025-01-31
```

Display all command options:

```powershell
vendas-cli --help
```

Use `-v` or `--verbose` to enable debug logs.

The report is written to stdout; informational and warning logs are written to stderr. Exit codes are `0` for success or help, `1` for file/CSV errors or an unavailable date filter, and `2` for invalid command usage or date arguments.

## CSV format

The required columns are `produto`, `quantidade`, and `preco_unitario`. A date column is optional and may be named `data`, `data_venda`, or `date`, with any capitalization.

Both variants are included in [`sample/`](sample/):

- [`vendas.csv`](sample/vendas.csv)
- [`vendas-with-date.csv`](sample/vendas-with-date.csv)

The reader accepts UTF-8 (including a BOM) and falls back to Latin-1. CRLF line endings are supported. Invalid data rows produce a warning and are skipped; the final log summarizes the rows read and skipped. If a date filter is requested but the CSV has no date column, the command reports an error instead of silently returning an unfiltered report.

## Report rules

- Monetary calculations use `Decimal` to avoid binary floating-point errors.
- The best-selling product is ranked by quantity sold, then total sales value. A complete tie is resolved alphabetically for consistent results.
- JSON output is UTF-8, preserves accented product names, and represents monetary values as numbers with exactly two decimal places.
- Date filtering uses inclusive start and end bounds. Sales without dates are excluded when a date bound is specified.

## Tests

Install the development dependencies, then run:

```powershell
python -m pytest
```

Pytest reports package coverage and requires at least 80%.
