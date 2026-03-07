.PHONY: render-catalog test

render-catalog:
	python scripts/render_skill_catalog.py

test:
	pytest -q
