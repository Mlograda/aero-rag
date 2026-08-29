"""M1 — corpus construction.

Turn ASRS Report Set PDFs into one JSONL file of individual incident reports.
Record schema: {"report_id", "topic", "narrative", "source_pdf"}

Gate: pytest tests/test_m1_corpus.py
"""
from pathlib import Path


def fetch_report_sets(urls: list[str], out_dir: Path) -> list[Path]:
    """Download ASRS report-set PDFs. Skip any file already on disk."""
    raise NotImplementedError


def pdf_to_reports(pdf_path: Path) -> list[dict]:
    """Split one report-set PDF into ~50 individual report records.

    Hint: read the extracted text of one PDF before writing this. There is a
    repeating delimiter. Find it, then write the splitter around it.
    """
    raise NotImplementedError


def build_corpus(pdf_dir: Path, out_path: Path) -> int:
    """Write all records to JSONL. Return the record count."""
    raise NotImplementedError
