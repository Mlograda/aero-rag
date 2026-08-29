"""M2 — chunk, embed, persist.

Chunk metadata MUST carry report_id through to the vector store, or M5 is
impossible and you will rebuild this.
"""
from pathlib import Path


def chunk_reports(records: list[dict], size: int, overlap: int) -> list[dict]:
    """Return chunks: {"chunk_id", "report_id", "text", "topic"}."""
    raise NotImplementedError


def build_index(chunks: list[dict], persist_dir: Path) -> None:
    raise NotImplementedError


def load_index(persist_dir: Path):
    raise NotImplementedError
