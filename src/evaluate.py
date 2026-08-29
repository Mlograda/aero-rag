"""M5 — evaluation. This is the project.

Reuse the judge pattern from your llm-evaluator repo for faithfulness.
"""
from pathlib import Path


def recall_at_k(results: list[list[str]], gold: list[list[str]], k: int) -> float:
    raise NotImplementedError


def mrr(results: list[list[str]], gold: list[list[str]]) -> float:
    raise NotImplementedError


def faithfulness(answer_text: str, contexts: list[str]) -> bool:
    """LLM-as-judge: is every claim in answer_text supported by contexts?"""
    raise NotImplementedError


def run_eval(questions_path: Path, out_path: Path) -> dict:
    """Write eval/results.json. Print the headline numbers."""
    raise NotImplementedError


if __name__ == "__main__":
    run_eval(Path("eval/questions.jsonl"), Path("eval/results.json"))
