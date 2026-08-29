# BUILD.md — Aviation Incident RAG

This is not a tutorial. There is no solution code in this repo.
Each milestone gives you: a goal, a contract (function signatures), a gate
(a test that must pass), and a time box. You write the code. The tests tell
you when you're done. Claude unblocks you when you're stuck.

Rule: you may not start milestone N+1 until milestone N's gate is green and committed.

---

## The corpus

NASA ASRS Database Report Sets — 30 topic sets, 50 real aviation incident
narratives each, free PDFs, public domain.

Index page: https://asrs.arc.nasa.gov/search/reportsets.html

Start with 8-10 sets (~400-500 reports). That's enough to make retrieval
non-trivial and small enough to iterate fast. Add more later if you want.

Why this corpus and not a Kaggle CSV: PDFs force real ingestion work
(extraction, splitting, metadata), the narratives are genuinely technical
and domain-specific, and it's the closest public analogue to the
maintenance/incident data you already understand professionally. Nobody
else's portfolio has it.

---

## M0 — Repo live (30 min)

Goal: public GitHub repo exists with this skeleton in it.

Gate:
- `git log` shows one commit
- `.gitignore` contains `.env` **in that first commit**
- repo is public and you have the URL

Do not polish. Ugly and public beats clean and local.

---

## M1 — Corpus (1 hour)

Goal: PDFs on disk → one JSONL file of individual reports.

Contract — `src/ingest.py`:
```
fetch_report_sets(urls: list[str], out_dir: Path) -> list[Path]
pdf_to_reports(pdf_path: Path) -> list[dict]
build_corpus(pdf_dir: Path, out_path: Path) -> int   # returns record count
```

Each record: `{"report_id", "topic", "narrative", "source_pdf"}`

The hard part is splitting one PDF into 50 records. Look at the structure of
the text before you write the splitter. `pdftotext -layout` or `pypdf` — your
choice, but look first.

Gate: `pytest tests/test_m1_corpus.py`

---

## M2 — Chunk, embed, index (2 hours)

Contract — `src/index.py`:
```
chunk_reports(records: list[dict], size: int, overlap: int) -> list[dict]
build_index(chunks: list[dict], persist_dir: Path) -> None
load_index(persist_dir: Path)
```

Chunk metadata must carry `report_id` through. If it doesn't, M5 is impossible
and you'll rebuild everything. Chroma + `text-embedding-3-small` is the cheap
default; anything persistent is fine.

Write down your chunk size and why, in `README.md`, now. You will change it in
M6 and you'll want the original reasoning.

Gate: `pytest tests/test_m2_index.py`

---

## M3 — Retrieval, hybrid (2 hours)

Contract — `src/retrieve.py`:
```
dense_search(query: str, k: int) -> list[dict]
bm25_search(query: str, k: int) -> list[dict]
hybrid_search(query: str, k: int) -> list[dict]   # reciprocal rank fusion
```

RRF is about six lines. Do not import a framework for it — writing it yourself
is the point, and it's an interview question.

Gate: `pytest tests/test_m3_retrieval.py` — for the 5 seeded probe questions in
`eval/probes.jsonl`, the gold `report_id` must appear in the top 5.

---

## M4 — Grounded generation (1.5 hours)

Contract — `src/generate.py`:
```
answer(query: str, k: int) -> dict   # {"answer", "citations": [report_id], "contexts": [...]}
```

Two non-negotiables:
1. Every factual sentence carries a `report_id` citation.
2. If the top retrieval scores are below threshold, it refuses. An assistant
   that answers "what is the capital of France" from an aviation corpus is a
   demo. One that refuses is a product.

Gate: `pytest tests/test_m4_generation.py`

---

## M5 — Evaluation (3 hours) — THIS IS THE PROJECT

Everything before this is table stakes. This is the part that gets callbacks.

Build `eval/questions.jsonl`: **50 questions you write by hand**, each labelled
with the `report_id`(s) that actually answer it. Read reports, write questions
from them. It's tedious. It is also the single strongest signal on your CV that
you have shipped with LLMs rather than watched videos. Do not generate them
with an LLM and skip the labelling.

Mix of question types — at minimum: 35 answerable, 10 answerable only by
combining two reports, 5 deliberately unanswerable (must trigger refusal).

Contract — `src/evaluate.py`:
```
recall_at_k(results, gold, k) -> float
mrr(results, gold) -> float
faithfulness(answer, contexts) -> bool   # LLM-as-judge — reuse your llm-evaluator
run_eval(questions_path, out_path) -> dict
```

Gate: `python -m src.evaluate` writes `eval/results.json`, and recall@5, MRR
and faithfulness % are pasted into README.md.

Whatever the numbers are, publish them. A README saying "recall@5 = 0.62, here
is where it fails and why" beats a README with no numbers, every time.

---

## M6 — Ablation (2 hours)

Change exactly one variable. Rerun the eval. Put a before/after table in the
README.

Options: chunk size 400→1000, add a cross-encoder reranker, dense-only vs
hybrid, different embedding model.

One table with two rows of real numbers is worth more than three extra
features. This is the milestone that makes you sound like an engineer instead
of a course graduate.

---

## M7 — Deploy (3 hours)

- FastAPI: `GET /health`, `POST /ask`
- Dockerfile, multi-stage, non-root user
- Deploy to Fly.io or Render (free tier is fine)
- Log per-request latency and token cost to stdout
- Public URL in the README

Gate: someone else can curl your endpoint and get an answer with citations.

---

## M8 — README as case study (1.5 hours)

Not a feature list. This structure:

1. Problem — 3 sentences
2. Architecture diagram — one image (Excalidraw is fine)
3. Design decisions and trade-offs — chunking, hybrid vs dense, refusal threshold
4. Evaluation — the numbers, the method, the labelled set
5. Ablation table
6. What it gets wrong — be honest, name three failure modes
7. Run it locally — 3 commands

Section 6 is the one hiring managers remember.

---

## Rules of engagement (how you ask me for help)

When you're stuck, send me:
1. What you're trying to do (one line)
2. The actual error, pasted in full
3. What you already tried
4. Your hypothesis, even if you think it's wrong

I give you a clue first, not code. If the clue doesn't unstick you within
15 minutes, ask again and I'll go one level more concrete. You'll get working
code from me only when you've hit the same wall twice.

I don't accept "I studied" or "I'm making progress." I accept commit hashes.

## Time box

Total ≈ 16 hours. At 2 evenings + one weekend morning per week that's three
weeks. If you're past week four, we cut scope — not deadline.
