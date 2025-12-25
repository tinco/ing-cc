import csv
import re
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable, List, Optional

from pypdf import PdfReader


@dataclass
class Transaction:
    date: str
    name: str
    notes: str
    type: str
    amount: Decimal


@dataclass
class Statement:
    label: str  # YYYY-MM
    transactions: List[Transaction]


TRANSACTION_PATTERN = re.compile(
    r"^(?P<date>\d{2}-\d{2}-\d{4})\s+"
    r"(?P<name>.+?)\s+"
    r"(?P<type>Betaling|Ontvangst|Incasso)\s+"
    r"(?P<sign>[+-])\s*"
    r"(?P<amount>\d+[.,]\d{2})$"
)

FOOTER_MARKERS = (
    re.compile(r"Geboekt op Naam", re.IGNORECASE),
    re.compile(r"Overeenkomstnummer", re.IGNORECASE),
    re.compile(r"Dit product valt", re.IGNORECASE),
    re.compile(r"Op ING.nl", re.IGNORECASE),
)

NOTE_WHITELIST_PREFIXES = (
    "Transactiedatum:",
    "Kaartnummer:",
    "Bedrag:",
    "Koers:",
    "Koersopslag",
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
    statement = parse_statement(path)
    return statement.transactions


def parse_statement(path: Path) -> Statement:
    reader = PdfReader(str(path))
    lines: List[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        lines.extend(text.splitlines())

    period_label = _extract_period_label(lines)

    matches = []
    for idx, line in enumerate(lines):
        m = TRANSACTION_PATTERN.match(line.strip())
        if m:
            matches.append((idx, m))

    transactions: List[Transaction] = []
    skip_keywords = (
        "Omschrijving",
        "Geboekt op Naam",
        "Overeenkomstnummer Periode",
        "Afschrift Creditcard",
        "pagina",
    )
    table_end = _find_table_end(lines, matches[-1][0]) if matches else len(lines)

    for current, (line_idx, match) in enumerate(matches):
        next_idx = matches[current + 1][0] if current + 1 < len(matches) else table_end
        end_idx = min(next_idx, table_end)
        note_lines = []
        for l in lines[line_idx + 1 : end_idx]:
            stripped = l.strip()
            if not stripped:
                continue
            if not _is_note_line(stripped):
                continue
            note_lines.append(stripped)
        notes = "\n".join(note_lines)
        amount = _normalize_amount(match.group("sign"), match.group("amount"))
        transactions.append(
            Transaction(
                date=match.group("date"),
                name=match.group("name").strip(),
                notes=notes,
                type=match.group("type"),
                amount=amount,
            )
        )

    label = period_label or _label_from_transactions(transactions)
    return Statement(label=label, transactions=transactions)


def _extract_period_label(lines: List[str]) -> Optional[str]:
    period_pattern = re.compile(
        r"Periode\s+(?P<start>\d{2}-\d{2}-\d{4})\s+t/m\s+(?P<end>\d{2}-\d{2}-\d{4})"
    )
    for line in lines:
        m = period_pattern.search(line)
        if m:
            start = datetime.strptime(m.group("start"), "%d-%m-%Y")
            return f"{start.year}-{start.month:02d}"
    return None


def _label_from_transactions(transactions: Iterable[Transaction]) -> str:
    dates = [datetime.strptime(tx.date, "%d-%m-%Y") for tx in transactions]
    if not dates:
        raise ValueError("No transactions found to derive label")
    earliest = min(dates)
    return f"{earliest.year}-{earliest.month:02d}"


def _find_table_end(lines: List[str], start_idx: int) -> int:
    for idx in range(start_idx, len(lines)):
        text = lines[idx]
        if any(pattern.search(text) for pattern in FOOTER_MARKERS):
            return idx
    return len(lines)


def _is_note_line(line: str) -> bool:
    return line.startswith(NOTE_WHITELIST_PREFIXES)


def write_csv(statement: Statement, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{statement.label}.csv"
    with output_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["date", "name", "notes", "type", "amount"])
        for tx in statement.transactions:
            writer.writerow([tx.date, tx.name, tx.notes, tx.type, f"{tx.amount:.2f}"])
    return output_path
