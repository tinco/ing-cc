ING Credit Card PDF to CSV
==========================

This is a small Python tool to convert ING credit card statement PDFs into CSV files. Each PDF becomes one CSV named `<YYYY>-<MM>.csv`, based on the statement period start date. Columns: `date,name,notes,type,amount`.

Development notes
- Written by OpenAI Codex.
- Built in a test-driven manner (`uv run pytest`).
- One statement month was manually checked for correctness by a human. Use at your own risk; no warranties are provided.
- Two years of transactions has been parsed and validated to be balanced.

Quickstart (with uv)
--------------------
1) Ensure `uv` is installed (see https://github.com/astral-sh/uv for installation).
2) In the project root, run:
```
uv run ing-cc --input pdfs --output out
```
   - `--input` defaults to `pdfs/`.
   - `--output` defaults to the current directory.
3) CSV files will appear in the output directory, one per PDF.

Testing
-------
```
uv run pytest
```

Analysis
--------
After generating CSVs (e.g., into `out/`), you can produce a per-statement summary JSON:
```
uv run ing-cc-analysis --input out --output analysis
```
This writes `analysis/summary.json` with, for each statement, the total spend (sum of outgoing payments), amount settled via `Incasso`, and the net difference (should be ~0).
