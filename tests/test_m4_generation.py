from src.generate import answer, REFUSAL

def test_answer_has_citations():
    out = answer("What happened during a cabin smoke event?")
    assert out["citations"], "Answer returned no citations."
    assert out["answer"].strip()

def test_refuses_out_of_scope():
    out = answer("What is the capital of France?")
    assert out["answer"].strip() == REFUSAL, \
        "The system answered a question the corpus cannot support. Add a score threshold."
    assert out["citations"] == []
