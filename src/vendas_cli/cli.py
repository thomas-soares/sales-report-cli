import argparse
import logging
import sys
from datetime import date
from pathlib import Path

from .core import generate_report
from .output import render
from .parser import CSVFormatError, parse_sales_csv

logger = logging.getLogger(__name__)


def _parse_date(value: str) -> date:
    try:
        parsed_date = date.fromisoformat(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD format") from error

    if parsed_date.isoformat() != value:
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD format")
    return parsed_date


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vendas-cli",
        description="Generate sales reports from CSV files.",
    )
    parser.add_argument("file", type=Path, help="path to the sales CSV file")
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        dest="output_format",
        help="report output format (default: text)",
    )
    parser.add_argument(
        "--start",
        type=_parse_date,
        metavar="YYYY-MM-DD",
        help="include sales on or after this date",
    )
    parser.add_argument(
        "--end",
        type=_parse_date,
        metavar="YYYY-MM-DD",
        help="include sales on or before this date",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="enable debug logging",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        if args.start is not None and args.end is not None and args.start > args.end:
            parser.error("--start must be on or before --end")
    except SystemExit as error:
        return error.code if isinstance(error.code, int) else 0

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
        force=True,
    )
    logger.debug("Reading CSV file: %s", args.file)

    try:
        parsed_csv = parse_sales_csv(args.file)
    except (OSError, CSVFormatError) as error:
        logger.error("Unable to read CSV file '%s': %s", args.file, error)
        return 1

    if (args.start is not None or args.end is not None) and not parsed_csv.has_date_column:
        logger.error("Cannot filter sales by date because the CSV has no date column.")
        return 1

    report = generate_report(parsed_csv.sales, args.start, args.end)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(render(report, args.output_format))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
