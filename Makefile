.PHONY: install m1 m2 m3 m4 eval serve
install:
	python -m venv .venv && .venv/bin/pip install -r requirements.txt
m1:
	pytest tests/test_m1_corpus.py -q
m2:
	pytest tests/test_m2_index.py -q
m3:
	pytest tests/test_m3_retrieval.py -q
m4:
	pytest tests/test_m4_generation.py -q
eval:
	python -m src.evaluate
serve:
	uvicorn src.app:app --reload
