from argparse import ArgumentParser
from pathlib import Path

from .parser import parse_pdf, write_csvs


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

    all_transactions = []
    for pdf in pdf_paths:
        all_transactions.extend(parse_pdf(pdf))

    write_csvs(all_transactions, args.output)
