"""M3 — hybrid retrieval.

Write reciprocal rank fusion yourself. It is ~6 lines and it is an interview
question. Do not import a framework for it.
"""


def dense_search(query: str, k: int = 5) -> list[dict]:
    raise NotImplementedError


def bm25_search(query: str, k: int = 5) -> list[dict]:
    raise NotImplementedError


def hybrid_search(query: str, k: int = 5) -> list[dict]:
    """Fuse dense + BM25 with RRF. Return [{"chunk_id","report_id","text","score"}]."""
    raise NotImplementedError
