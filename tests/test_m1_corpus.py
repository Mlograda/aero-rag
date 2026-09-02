import json
from pathlib import Path
import pytest

CORPUS = Path("data/corpus.jsonl")

def load():
    if not CORPUS.exists():
        pytest.fail("data/corpus.jsonl does not exist yet — build_corpus() has not run.")
    return [json.loads(l) for l in CORPUS.read_text().splitlines() if l.strip()]

def test_enough_records():
    assert len(load()) >= 50, "Ingest at least 8 report sets (~400 records)."

def test_schema():
    for r in load()[:50]:
        assert {"report_id", "topic", "narrative", "source_pdf"} <= r.keys()

def test_narratives_are_real():
    recs = load()
    assert all(len(r["narrative"].strip()) > 50 for r in recs[:50]), \
        "Some narratives are near-empty — your PDF splitter is cutting wrong."

def test_report_ids_unique():
    ids = [r["report_id"] for r in load()]
    assert len(ids) == len(set(ids)), "Duplicate report_ids — splitter is misfiring."
