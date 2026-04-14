
1) Why I chose this chunk size

I used:

- `CHUNK_SIZE_CHARS = 2000`
- `CHUNK_OVERLAP_CHARS = 300`

### Reasoning
- If chunks are too small, context gets fragmented and retrieval may miss connected ideas.
- If chunks are too large, embeddings become less specific and retrieval precision drops.
- Around 1500–2500 characters is a practical balance for mixed documents (resume-style, reports, and notes).
- A 300-character overlap helps preserve continuity between neighboring chunks (e.g., section transitions or split sentences).

This setting gave good retrieval quality in my local tests while keeping latency acceptable.

---

## 2) One retrieval failure case observed

### Failure case
When I asked a vague query such as:

> “Which topic is best in this resume?”

the retriever sometimes returned a chunk that was semantically related to “resume” but not specific enough to answer “best topic” reliably.

### Why this happened
- The query is subjective (“best”) and not tied to a precise factual span.
- Vector similarity can retrieve nearest semantic content, but not always intent-perfect content for ambiguous questions.

### Mitigation
- Ask a more specific question (e.g., “Which technical skills are most emphasized in this resume?”).
- Increase `top_k` to gather more candidate context.
- (Future) Add reranking or query rewriting for ambiguous prompts.

---

## 3) One metric tracked

I tracked **latency** in the `/qa/ask` response:

- `embedding_ms`
- `retrieval_ms`
- `generation_ms`
- `total_ms`

I also surfaced retrieval `score` per returned source chunk.

### Why this metric matters
- Helps identify bottlenecks (embedding vs retrieval vs generation).
- Useful for optimization and for judging practical API responsiveness.