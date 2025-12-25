from decimal import Decimal
from pathlib import Path

from ing_cc.parser import parse_pdf, write_csvs


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
    transactions = parse_pdf(Path("pdfs/AFSCHRIFT.pdf"))

    write_csvs(transactions, tmp_path)

    june_file = tmp_path / "06-2023.csv"
    july_file = tmp_path / "07-2023.csv"

    assert june_file.exists()
    assert july_file.exists()

    june_lines = june_file.read_text(encoding="utf-8").splitlines()
    assert june_lines[0] == "date,name,description,notes,type,amount"
    assert any("30-06-2023" in line for line in june_lines[1:])

