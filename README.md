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

Each CSV is named `<MM>-<YYYY>.csv` and contains: `date,name,description,notes,type,amount`.
