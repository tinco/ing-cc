set shell := ["bash", "-c"]

default: cc

run:
	uv run ing-cc --input pdfs --output out

analyze:
	uv run ing-cc-analysis --input out --output analysis

cc:
	just run
	just analyze
	@tmp=$(mktemp); \
	first=$(ls out/*.csv | head -n 1); \
	head -n 1 "$first" > "$tmp"; \
	for f in out/*.csv; do tail -n +2 "$f"; done >> "$tmp"; \
	mv "$tmp" cc.csv
	cat analysis/summary.json
