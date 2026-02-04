"""Hybrid retriever using Elasticsearch RRF (Reciprocal Rank Fusion).

Combines BM25 text search with dense vector kNN search.
Uses ES 8.14+ RRF support with rank_constant=60.
"""

import os

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

from ingest.embedding import embed_query

load_dotenv()

INDEX_NAME = "wiki-hybrid"


def get_es_client() -> Elasticsearch:
    return Elasticsearch(
        os.getenv("ELASTIC_ENDPOINT"),
        api_key=os.getenv("ELASTIC_API_KEY"),
        request_timeout=30,
    )


def search(query: str, top_k: int = 10, candidate_size: int = 50) -> list[dict]:
    """RRF hybrid search combining BM25 + kNN.

    Args:
        query: Search query string.
        top_k: Number of results to return.
        candidate_size: Number of kNN candidates before RRF fusion.

    Returns:
        list[dict], each dict has keys: "id", "text", "score", "method".
        "method" should be "Hybrid (RRF)".

    Hints:
        - Use embed_query(query) to get the query embedding vector
        - Use get_es_client() and es.search() with "retriever" parameter
        - RRF retriever combines "standard" (BM25 match) + "knn" retrievers
        - kNN field: "embedding", rank_constant: 60
        - num_candidates = candidate_size * 2
    """
    es = get_es_client()
    query_vec = embed_query(query)

    resp = es.search(
        index=INDEX_NAME,
        size=top_k,
        retriever={
            "rrf": {
                "rank_constant": 60,
                "retrievers": [
                    {"standard": {"query": {"match": {"text": query}}}},
                    {
                        "knn": {
                            "field": "embedding",
                            "query_vector": query_vec,
                            "k": candidate_size,
                            "num_candidates": candidate_size * 2,
                        }
                    },
                ],
            }
        },
    )

    hits = resp.get("hits", {}).get("hits", [])
    results = []
    for hit in hits:
        source = hit.get("_source", {})
        results.append({
            "id": hit.get("_id", ""),
            "text": source.get("text", ""),
            "score": hit.get("_score", 0.0),
            "method": "Hybrid (RRF)",
        })
    return results
