# Aviation Incident RAG

<!-- Rewrite this whole file at M8. Until then it is a placeholder so the repo
     is not empty. Do NOT spend time on it before the code works. -->

Retrieval-augmented question answering over NASA ASRS aviation incident reports,
with hybrid retrieval, grounded citations, and a hand-labelled evaluation set.

Status: in progress. See BUILD.md for the milestone plan.

## Design decisions
- Chunk size: M2 reasoning: cap at 3,000 characters, chosen because the median is 1,655 and the distribution has no natural break. There are 32 out of 150 (21%) reports with more than 3000 characters (decision: these will be chunked with overlap) and 79% of reports stay intact (embedded as a whole) and five retrieved chunks fit comfortably in context (3000x5 = 15000 characters). cap size; 3000, Overlap size: 200 characters

## Evaluation
- recall@5: TBD
- MRR: TBD
- faithfulness: TBD
