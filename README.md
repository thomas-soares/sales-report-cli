# Sales Report CLI

A Python command-line application for generating sales reports from CSV data.

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

Use `--help` to display the command-line options.

## CSV structure

Sales data uses these columns:

- `produto`
- `quantidade`
- `preco_unitario`
- optional `data`

The sample files in `sample/` show both required and optional-date variants:

- [`sample/vendas.csv`](sample/vendas.csv)
- [`sample/vendas-with-date.csv`](sample/vendas-with-date.csv)

## Business assumptions

- Monetary values use `Decimal` to avoid floating-point precision issues.
- The best-selling product is determined by quantity first, and by the total value if quantities tie.
- If a date column is present, it is expected to use the `YYYY-MM-DD` format.

## Project layout

```text
src/
  vendas_cli/
    __init__.py
    cli.py
    models.py
tests/
  test_models.py
sample/
  vendas.csv
  vendas-with-date.csv
```
