from decimal import Decimal
from pathlib import Path

from ing_cc.parser import parse_pdf, parse_statement, write_csv


def test_parse_pdf_extracts_transactions():
    pdf_path = Path("pdfs/AFSCHRIFT.pdf")
    transactions = parse_pdf(pdf_path)

    assert len(transactions) == 20

    first = transactions[0]
    assert first.date == "03-07-2023"
    assert first.name == "AFLOSSING"
    assert first.type == "Incasso"
    assert first.amount == Decimal("397.09")
    assert "Kaartnummer" in first.notes

    payment = transactions[1]
    assert payment.name.startswith("WEBFLOW.COM")
    assert payment.amount == Decimal("-20.51")


def test_write_csvs_creates_monthly_files(tmp_path):
    statement = parse_statement(Path("pdfs/AFSCHRIFT.pdf"))

    csv_path = write_csv(statement, tmp_path)

    assert csv_path.name == "2023-06.csv"
    lines = csv_path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "date,name,notes,type,amount"
    assert any("30-06-2023" in line for line in lines[1:])
    # July transactions in the same statement also belong in this CSV
    assert any("03-07-2023" in line for line in lines[1:])


def test_no_header_text_leaks_into_notes(tmp_path):
    statement = parse_statement(Path("pdfs/AFSCHRIFT.pdf"))
    write_csv(statement, tmp_path)

    for csv_path in tmp_path.glob("*.csv"):
        content = csv_path.read_text(encoding="utf-8")
        assert "Omschrijving" not in content


def test_newer_format_without_space_between_sign_and_amount(tmp_path):
    statement = parse_statement(Path("pdfs/AFSCHRIFT-1.pdf"))
    assert statement.label == "2025-11"
    assert len(statement.transactions) > 0

    first = statement.transactions[0]
    assert first.amount == Decimal("688.77")
    assert first.type == "Incasso"
    assert "Kaartnummer" in first.notes

    csv_path = write_csv(statement, tmp_path)
    content = csv_path.read_text(encoding="utf-8")
    assert "688.77" in content  # amount captured even without space


def test_thousands_separator_amounts_are_parsed(tmp_path):
    statement = parse_statement(Path("pdfs/AFSCHRIFT-21.pdf"))
    # First transaction is an Incasso with a thousands separator.
    assert any(tx.type == "Incasso" and tx.amount == Decimal("1231.28") for tx in statement.transactions)
    # Cash withdrawal and fee should also be captured.
    assert any(tx.type == "Geldopname" and tx.amount == Decimal("-180.00") for tx in statement.transactions)
    assert any(tx.type == "Kosten" and tx.amount == Decimal("-7.20") for tx in statement.transactions)

    csv_path = write_csv(statement, tmp_path)
    data = csv_path.read_text(encoding="utf-8")
    flat = data.replace(",", ".")
    assert "1231.28" in flat
    assert "180.00" in flat
    assert "7.20" in flat


def test_correctie_transaction_is_captured(tmp_path):
    statement = parse_statement(Path("pdfs/AFSCHRIFT-28.pdf"))
    assert statement.label == "2023-09"
    assert any(tx.type == "Correctie" and tx.amount == Decimal("1733.49") for tx in statement.transactions)
    csv_path = write_csv(statement, tmp_path)
    content = csv_path.read_text(encoding="utf-8")
    assert "1733.49" in content.replace(",", ".")
