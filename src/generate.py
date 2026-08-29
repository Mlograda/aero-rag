"""M4 — grounded answers with citations and refusal."""

REFUSAL = "I could not find this in the incident reports."


def answer(query: str, k: int = 5) -> dict:
    """Return {"answer", "citations": [report_id], "contexts": [...]}.

    Two non-negotiables:
      1. every factual claim carries a report_id citation
      2. below the retrieval-score threshold, return REFUSAL with no citations
    """
    raise NotImplementedError
