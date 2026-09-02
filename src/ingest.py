"""M1 — corpus construction.

Turn ASRS Report Set PDFs into one JSONL file of individual incident reports.
"""
from pathlib import Path
import json

from pypdf import PdfReader


def save_records(records: list[dict], path: Path) -> None:
    """Write records to JSONL — one JSON object per line."""
    with open(path, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def load_records(path: Path) -> list[dict]:
    """Read a JSONL file back into a list of records."""
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def pdf_to_reports(pdf_path: Path) -> list[dict]:
    """Split one ASRS report-set PDF into individual report records.

    The PDF has two sections: 50 short synopses, then 50 full records.
    Each ACN appears once per section, so the full records start at
    index 1 + (occurrences / 2).
    """
    reader = PdfReader(pdf_path)
    full = "\n".join(p.extract_text() or "" for p in reader.pages)

    parts = full.split("ACN:")
    n_records = (len(parts) - 1) // 2
    blocks = parts[1 + n_records:]

    if len(blocks) != n_records:
        raise ValueError(f"Expected {n_records} blocks, got {len(blocks)}")

    records = []
    for b in blocks:
        report_id = b.split("(")[0].strip()

        inc_fields = {}
        for item in b.split("\n"):
            if " : " not in item:
                continue
            key, value = item.split(" : ", 1)
            inc_fields.setdefault(key.strip(), []).append(value.strip())

        if "Narrative: 1" not in b:
            raise ValueError(f"No narrative found in report {report_id}")

        narrative_fields = b.split("Narrative: 1", 1)[1]
        end = narrative_fields.find("Synopsis")
        if end == -1:
            end = len(narrative_fields)
        narrative = narrative_fields[:end].strip()

        records.append({
            "report_id": report_id,
            "narrative": narrative,
            "aircraft": inc_fields.get("Make Model Name", []),
            "flight_phase": inc_fields.get("Flight Phase", []),
            "primary_problem": inc_fields.get("Primary Problem", []),
            "fields": inc_fields,
            "source_pdf": Path(pdf_path).name,
            "topic": Path(pdf_path).stem,
        })

    return records


def build_corpus(pdf_dir: Path, out_path: Path) -> int:
    """Parse every PDF in pdf_dir into one JSONL corpus. Returns record count."""
    pdf_dir = Path(pdf_dir)
    records = []
    for pdf_path in sorted(pdf_dir.glob("*.pdf")):
        records.extend(pdf_to_reports(pdf_path))
    save_records(records, out_path)
    return len(records)


if __name__ == "__main__":
    n = build_corpus(Path("data/pdfs"), Path("data/corpus.jsonl"))
    print(f"{n} records written to data/corpus.jsonl")