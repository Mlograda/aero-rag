import json
from pathlib import Path
import pytest
from src.retrieve import hybrid_search, dense_search, bm25_search

PROBES = Path("eval/probes.jsonl")

def probes():
    rows = [json.loads(l) for l in PROBES.read_text().splitlines() if l.strip()]
    rows = [r for r in rows if "question" in r]
    if any(r["question"] == "REPLACE ME" for r in rows):
        pytest.fail("eval/probes.jsonl still has placeholders — write 5 real probe questions.")
    return rows

@pytest.mark.parametrize("fn", [dense_search, bm25_search, hybrid_search])
def test_returns_k(fn):
    assert len(fn("engine fire during climb", k=5)) == 5

def test_hybrid_beats_placeholder():
    hits = 0
    for p in probes():
        got = [r["report_id"] for r in hybrid_search(p["question"], k=5)]
        if any(g in got for g in p["gold_report_ids"]):
            hits += 1
    assert hits >= 4, f"Only {hits}/5 probes retrieved their gold report in top-5."
