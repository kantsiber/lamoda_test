import os
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

all_docs = []
for file in os.listdir("articles"):
    with open(f"articles/{file}", "r", encoding="utf-8") as f:
        text = f.read()
        all_docs.append({"text": text, "source": file})

print(f"загружено статей: {len(all_docs)}")

tokenizer_docs = []
for doc in all_docs:
    tokens = doc["text"].lower().split()
    tokenizer_docs.append(tokens)

bm25 = BM25Okapi(tokenizer_docs)

def search_bm25(query: str, top_k=3) -> list:
    query_tokens = query.lower().split()
    scores = bm25.get_scores(query_tokens)
    top_index = np.argsort(scores)[::-1][:top_k]

    results = []
    for i in top_index:
        results.append({
            "source": all_docs[i]["source"],
            "score": scores[i],
            "text": all_docs[i]["text"][:100]
        })
    return results


model = SentenceTransformer('ai-forever/sbert_large_nlu_ru')

texts = [doc["text"] for doc in all_docs]
text_embeddings = model.encode(texts, show_progress_bar=True)

def search_dense(query: str, top_k=3) -> list:
    query_embeddings = model.encode([query])
    scores = cosine_similarity(query_embeddings, text_embeddings)[0]
    top_index = np.argsort(scores)[::-1][:top_k]

    result = []
    for i in top_index:
        result.append({
            "source": all_docs[i]["source"],
            "score": scores[i],
            "text": all_docs[i]["text"][:100]
        })

    return result

def search_hybrid(query: str, top_k=3, bm25_weight=0.5, dense_weight=0.5) -> list:
    bm25_results = search_bm25(query, top_k=len(all_docs))
    dense_results = search_dense(query, top_k=len(all_docs))

    bm25_scores = {r["source"]: r["score"] for r in bm25_results}
    dense_scores = {r["source"]: r["score"] for r in dense_results}

    bm25_max = max(bm25_scores.values())
    dense_max = max(dense_scores.values())

    combined = {}
    for source in bm25_scores:
        b_score = bm25_scores[source] / bm25_max if bm25_max > 0 else 0
        d_score = dense_scores[source] / dense_max if dense_max > 0 else 0
        combined[source] = bm25_weight * b_score + dense_weight * d_score

    top_sources = sorted(combined, key=combined.get, reverse=True)[:top_k]

    results = []
    for source in top_sources:
        idx = next(i for i, d in enumerate(all_docs) if d["source"] == source)
        results.append({
            "source": source,
            "score": combined[source],
            "text": all_docs[idx]["text"][:200]
        })
    return results

for r in search_hybrid("как зарегистрироваться"):
    print(f"Score: {r['score']:.2f} | {r['source']}")