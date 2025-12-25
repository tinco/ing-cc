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
