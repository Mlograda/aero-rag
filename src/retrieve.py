"""M3 — hybrid retrieval.

Write reciprocal rank fusion yourself. It is ~6 lines and it is an interview
question. Do not import a framework for it.
"""


def dense_search(query: str, k: int = 5) -> list[dict]:
    raise NotImplementedError


def bm25_search(query: str, k: int = 5) -> list[dict]:
    raise NotImplementedError


def hybrid_search(query: str, k: int = 5, fetch_k: int = 50,
                  filters: dict | None = None,
                  filter_mode: str = "soft") -> list[dict]:
    """Fuse dense + BM25 with RRF, then apply metadata filtering.

    fetch_k is the candidate pool; k is what's returned. Boosting can only
    reorder what was retrieved, so fetch_k must be well above k.

    filter_mode "hard" drops non-matching candidates; "soft" boosts matches.
    """
    raise NotImplementedError
