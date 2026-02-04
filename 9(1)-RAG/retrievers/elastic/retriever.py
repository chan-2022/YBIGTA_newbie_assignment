"""BM25 retriever using Elasticsearch."""

import os

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv()

INDEX_NAME = "wiki-bm25"


def get_es_client() -> Elasticsearch:
    return Elasticsearch(
        os.getenv("ELASTIC_ENDPOINT"),
        api_key=os.getenv("ELASTIC_API_KEY"),
        request_timeout=30,
    )


def search(query: str, top_k: int = 10) -> list[dict]:
    """BM25 match search.

    Args:
        query: Search query string.
        top_k: Number of results to return.

    Returns:
        list[dict], each dict has keys: "id", "text", "score", "method".
        "method" should be "BM25".

    Hints:
        - Use get_es_client() and es.search()
        - Index name: INDEX_NAME
        - Use "match" query on "text" field
    """
    es = get_es_client()
    resp = es.search(
        index=INDEX_NAME,
        size=top_k,
        query={"match": {"text": query}},
    )
    hits = resp.get("hits", {}).get("hits", [])
    results = []
    for hit in hits:
        source = hit.get("_source", {})
        results.append({
            "id": hit.get("_id", ""),
            "text": source.get("text", ""),
            "score": hit.get("_score", 0.0),
            "method": "BM25",
        })
    return results
