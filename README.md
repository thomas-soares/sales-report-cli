# Sales Report CLI

A Python package for loading sales data from CSV files, calculating sales reports, and rendering text or JSON output.

## Requirements

- Python 3.10 or newer
- `pip` for installation

## Installation

```bash
python -m pip install -e ".[dev]"
```

You can also install it in standard mode:

```bash
python -m pip install .
```

## Command

```bash
vendas-cli --help
```

The installed command currently provides its help output. The package APIs can be used from Python:

```python
from vendas_cli.core import generate_report
from vendas_cli.output import render
from vendas_cli.parser import parse_sales_csv

parsed = parse_sales_csv("sample/vendas.csv")
report = generate_report(parsed.sales)
print(render(report))
```

## CSV structure

Sales data must include these columns:

- `produto`
- `quantidade`
- `preco_unitario`
- optional `data`

The `data` column is optional. The sample files in `sample/` show both variants:

- [`sample/vendas.csv`](sample/vendas.csv)
- [`sample/vendas-with-date.csv`](sample/vendas-with-date.csv)

## Business assumptions

- Dates are optional because the supplied sales data has no date column. If a date bound is applied, undated rows cannot be included reliably and are excluded.
- The date column accepts `data`, `data_venda`, or `date`, regardless of capitalization, to accommodate common header variants.
- CSV input is decoded as UTF-8 with an optional BOM, falling back to Latin-1 so legacy accented names can be read without an encoding option. CRLF line endings are supported for files created on Windows.
- Invalid rows produce a warning and are skipped so valid rows can still be reported, while the log makes the ignored data visible.
- Monetary values use `Decimal` to avoid binary floating-point precision errors in financial totals.
- The best-selling product is ranked by quantity, then total sales value. Alphabetical product name resolves a complete tie so results remain consistent.
- JSON monetary values are numbers formatted with two decimal places for predictable consumption by other software.

## Project layout

```text
src/
  vendas_cli/
    __init__.py
    cli.py
    core.py
    models.py
    output.py
    parser.py
tests/
  test_core.py
  test_models.py
  test_output.py
  test_parser.py
sample/
  vendas.csv
  vendas-with-date.csv
```
