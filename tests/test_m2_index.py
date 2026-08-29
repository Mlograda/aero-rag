from pathlib import Path
import pytest
from src.index import load_index

PERSIST = Path("storage")

def test_index_exists():
    if not PERSIST.exists():
        pytest.fail("No persisted index at storage/ — build_index() has not run.")

def test_index_has_chunks():
    idx = load_index(PERSIST)
    assert idx is not None

def test_chunks_carry_report_id():
    """If this fails, stop and fix it now. Evaluation is impossible without it."""
    idx = load_index(PERSIST)
    sample = idx.get(limit=5)
    metas = sample["metadatas"] if isinstance(sample, dict) else sample
    assert all("report_id" in m for m in metas), \
        "Chunk metadata is missing report_id — M5 cannot work without it."
