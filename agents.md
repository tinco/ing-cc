Notes for agents
----------------

- Use `uv run <command>` to execute project code and `uv run pytest` for tests; no extra environment variables are needed.
- Project script entry point: `uv run ing-cc` (reads PDFs from `pdfs/`, writes CSVs to CWD).
- Dependencies are managed by uv via `pyproject.toml`; add packages with `uv add ...` or `uv add --dev ...`.
- Prefer `uv run python` for ad-hoc Python snippets; avoid touching uv cache or adding custom env vars unless absolutely required.
