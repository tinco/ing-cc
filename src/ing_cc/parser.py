import csv
import re
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable, List

from pypdf import PdfReader


@dataclass
class Transaction:
    date: str
    name: str
    description: str
    notes: str
    type: str
    amount: Decimal


TRANSACTION_PATTERN = re.compile(
    r"^(?P<date>\d{2}-\d{2}-\d{4})\s+"
    r"(?P<name>.+?)\s+"
    r"(?P<type>Betaling|Ontvangst|Incasso)\s+"
    r"(?P<sign>[+-])\s+"
    r"(?P<amount>\d+[.,]\d{2})$"
)


def _normalize_amount(sign: str, value: str) -> Decimal:
    try:
        amount = Decimal(value.replace(".", "").replace(",", "."))
    except InvalidOperation as exc:
        raise ValueError(f"Invalid amount value: {value}") from exc
    if sign == "-":
        return -amount
    return amount


def parse_pdf(path: Path) -> List[Transaction]:
    reader = PdfReader(str(path))
    lines: List[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        lines.extend(text.splitlines())

    matches = []
    for idx, line in enumerate(lines):
        m = TRANSACTION_PATTERN.match(line.strip())
        if m:
            matches.append((idx, m))

    transactions: List[Transaction] = []
    for current, (line_idx, match) in enumerate(matches):
        next_idx = matches[current + 1][0] if current + 1 < len(matches) else len(lines)
        note_lines = [l.strip() for l in lines[line_idx + 1 : next_idx] if l.strip()]
        notes = "\n".join(note_lines)
        amount = _normalize_amount(match.group("sign"), match.group("amount"))
        transactions.append(
            Transaction(
                date=match.group("date"),
                name=match.group("name").strip(),
                description="",
                notes=notes,
                type=match.group("type"),
                amount=amount,
            )
        )

    return transactions


def transactions_by_month(transactions: Iterable[Transaction]):
    buckets = {}
    for tx in transactions:
        dt = datetime.strptime(tx.date, "%d-%m-%Y")
        key = f"{dt.month:02d}-{dt.year}"
        buckets.setdefault(key, []).append(tx)
    return buckets


def write_csvs(transactions: Iterable[Transaction], output_dir: Path) -> None:
    buckets = transactions_by_month(transactions)
    output_dir.mkdir(parents=True, exist_ok=True)
    for bucket, items in buckets.items():
        output_path = output_dir / f"{bucket}.csv"
        with output_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["date", "name", "description", "notes", "type", "amount"])
            for tx in items:
                writer.writerow(
                    [tx.date, tx.name, tx.description, tx.notes, tx.type, f"{tx.amount:.2f}"]
                )

