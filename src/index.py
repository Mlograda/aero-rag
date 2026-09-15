"""M2 — chunk, embed, persist.

Chunk metadata MUST carry report_id through to the vector store, or M5 is
impossible and you will rebuild this.
"""
from pathlib import Path
import os 
from dotenv import load_dotenv
from openai  import OpenAI
import chromadb

# Load the key
load_dotenv()
key = os.getenv("OPENAI_API_KEY")
if not key:
    raise RuntimeError("OPENAI_API_KEY not found — check your .env file")
client = OpenAI(api_key=key)

### HELPER FUNCTIONS 
def split_text(text: str, size: int = 3000, overlap: int = 200) -> list[str]:
    """Split text into overlapping windows of at most `size` characters.

    Each window starts `size - overlap` characters after the previous one, so
    consecutive pieces share `overlap` characters. The overlap exists so that a
    sentence falling on a boundary still appears intact in one of the two
    pieces — without it, cause and effect can end up in separate chunks and
    neither answers the question.

    The loop stops as soon as a window reaches the end of the text. Without
    that check, a final window starting inside the previous overlap would
    produce a short chunk whose content is already fully contained in the
    piece before it.

    Text shorter than `size` is returned as a single piece.
    """
    pieces = []
    start = 0
    while start < len(text):
        end = start + size
        pieces.append(text[start:end])
        if end >= len(text):
            break
        start = start + size - overlap
    return pieces

# batch then embed ; API calls have a token limit 
def embed_texts(texts, batch_size=100)-> list[list[float]]:
    """Embed texts, returning one vector per text in the same order.

    Batched because one call per text is slow, and one call for everything
    hits the API's per-request token limit as the corpus grows.

    Order is the only link between a vector and its text — if it were ever
    lost, every chunk would get the wrong vector and nothing would raise.
    """
    vectors = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        resp = client.embeddings.create(
            model ="text-embedding-3-small",
            input=batch
        )
        vectors.extend(d.embedding for d in resp.data)
    return vectors

### MAIN FUNCTIONS

def chunk_reports(records: list[dict], size: int = 3000, overlap: int = 200) -> list[dict]:
    """Return chunks: {"chunk_id", "report_id", "text", "topic"}."""
    chunks = []
    for r in records: 
        pieces = split_text(r["narrative"], size, overlap) if len(r["narrative"]) > size else [r["narrative"]]
        for i, piece in enumerate(pieces):
            chunks.append({
                "chunk_id": f"{r['report_id']}_{i:02d}",
                "report_id": r['report_id'],
                "text": piece,
                "aircraft": r["aircraft"],
                "flight_phase": r["flight_phase"],
                "primary_problem": r["primary_problem"],
                "topic": r["topic"],
            })
    return chunks

def build_index(chunks: list[dict], persist_dir: Path, name="asrs") -> int:
    # Send the chunk texts to the embedding model 
    # Retrieve texts form chunks 
    texts = [c["text"] for c in chunks]
    # Embed texts
    vectors = embed_texts(texts)

    # Create a chroma collection that saves to disk 
    chroma = chromadb.PersistentClient(path=str(persist_dir))
    collection = chroma.get_or_create_collection(name)

    # Add each chunk with its ID, text , and metadata
    collection.upsert( # used upsert to avoid duplicate IDs 
        ids=[c["chunk_id"] for c in chunks],
        documents=texts,
        embeddings=vectors,
        metadatas=[{
            "report_id": c["report_id"],
            "aircraft": "|".join(c["aircraft"]),    # Flattened to a string. Chroma's `where` filter only does exact equality —
                                                    # it cannot answer "does this chunk involve an A321?" when the value is a
                                                    # list. Tested: a scalar filter does not match list members. So metadata
                                                    # matching happens in our own code in M3, after retrieval, splitting on "|".
            "flight_phase": "|".join(c["flight_phase"]),
            "primary_problem": "|".join(c["primary_problem"]),
            "topic": c["topic"],
        } for c in chunks],
    )
    return collection.count()

def load_index(persist_dir: Path, name: str = "asrs")-> chromadb.Collection:
    """Open an existing Chroma collection from disk.

    Separate from build_index because embedding costs money and takes time.
    Build once; every later query loads from disk.
    """
    chroma = chromadb.PersistentClient(path=str(persist_dir))
    return chroma.get_collection(name)
