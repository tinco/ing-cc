from argparse import ArgumentParser
from pathlib import Path

from .parser import parse_statement, write_csv


def main() -> None:
    parser = ArgumentParser(description="Convert ING credit card statements (PDF) to CSV.")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("pdfs"),
        help="Directory containing ING credit card statement PDFs (default: %(default)s)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("."),
        help="Directory to write CSV files into (default: current directory)",
    )
    args = parser.parse_args()

    pdf_paths = sorted(p for p in args.input.glob("*.pdf") if p.is_file())
    if not pdf_paths:
        raise SystemExit(f"No PDF statements found in {args.input}")

    for pdf in pdf_paths:
        statement = parse_statement(pdf)
        write_csv(statement, args.output)
