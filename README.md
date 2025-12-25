ING credit card statement to CSV converter
==========================================

Usage
-----

- Convert all PDFs in `pdfs/` and write monthly CSVs to the project root:

```
uv run ing-cc
```

- Choose input/output directories:

```
uv run ing-cc --input pdfs --output out
```

- Each PDF produces exactly one CSV, named `<YYYY>-<MM>.csv` based on the statement period start date.
- Columns: `date,name,notes,type,amount`.
