"""M3 — hybrid retrieval.

Write reciprocal rank fusion yourself. It is ~6 lines and it is an interview
question. Do not import a framework for it.
"""
import numpy as np 
import chromadb
from rank_bm25 import BM25Okapi
from src.index import embed_texts


def dense_search(query: str, collection: chromadb.Collection,  k: int = 5) -> list[dict]:
    qvec = embed_texts([query])[0]
    res = collection.query(query_embeddings=[qvec], n_results=k)
    return [
        {"chunk_id": cid, "report_id": m["report_id"], "text": doc, "score": 1 - dist} # Chroma returns a distance (small = close). Invert it so `score` means the
                                                                                        # same thing here as in bm25_search: higher is better.
        for cid, doc, m, dist in zip(
            res["ids"][0], res["documents"][0], res["metadatas"][0], res["distances"][0]
        )
    ]

def build_bm25(chunks: list[dict]) -> BM25Okapi: 
    """Build the keyword index from chunk texts.

    Separate from search because the index depends only on the corpus, not the
    query. Rebuilding it per query means re-tokenising every chunk each time —
    fine for one query, wasteful for the 50-question evaluation in M5.

    Unlike the vector index this is not persisted; it is cheap to rebuild at
    the start of a session.
    """
    # Turn every chunk's text into a list of lowercase words.
    #  BM25 works on tokens, not raw strings.
    corpus_tokens = [c["text"].lower().split() for  c in chunks]

    # Build the BM25 object from those token lists.
    return  BM25Okapi(corpus_tokens)


def bm25_search(query: str, bm25: BM25Okapi, chunks: list[dict], k: int = 5) -> list[dict]:
    """Keyword search over the chunks. Returns the same shape as dense_search.

    `bm25` and `chunks` must come from the same call to build_bm25 — the scores
    are returned by position, so a mismatched list would map scores to the
    wrong chunks with no error.

    Complements dense search: strong on rare exact terms (part numbers, codes,
    aircraft types) that mean nothing to an embedding model, weak on questions
    reworded in different vocabulary.
    """
    # Tokenise the query the same way.
    #  It must match the corpus_tokens exactly, or words won't line up.
    query_token = query.lower().split()

    # Get the scores. One score per chunk, in the same order as `chunks`.
    scores = bm25.get_scores(query_token)
    # Find the positions of the k highest scores.
    top = np.argsort(scores)[::-1][:k]

    # For each of those positions, build a result dict:
    #  chunk_id, report_id, text, score — taken from chunks[position].
    top_results = []
    for i in top:
        top_results.append({
            "chunk_id" : chunks[i]["chunk_id"],
            "report_id" : chunks[i]["report_id"],
            "text": chunks[i]["text"],
            "score": float(scores[i])
        })
    # Return the list, highest score first.
    return top_results


def hybrid_search(query: str, k: int = 5, fetch_k: int = 50,
                  filters: dict | None = None,
                  filter_mode: str = "soft") -> list[dict]:
    """Fuse dense + BM25 with RRF, then apply metadata filtering.

    fetch_k is the candidate pool; k is what's returned. Boosting can only
    reorder what was retrieved, so fetch_k must be well above k.

    filter_mode "hard" drops non-matching candidates; "soft" boosts matches.
    """
    raise NotImplementedError



