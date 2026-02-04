"""Upstage Solar embedding utility with disk caching and parallel API keys.

Models:
  - solar-embedding-1-large-passage  (document encoding)
  - solar-embedding-1-large-query    (query encoding)

Uses multiple API keys (UPSTAGE_API_KEY1..N) for parallel embedding.
Each key gets its own thread with independent RPM/TPM limits.
Saves progress incrementally so crashes don't lose work.
Cache: data/processed/embeddings.npy (float32) + embedding_ids.json
"""

import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, wait
from pathlib import Path
from threading import Lock

import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm

load_dotenv()

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
EMBEDDINGS_PATH = PROCESSED_DIR / "embeddings.npy"
IDS_PATH = PROCESSED_DIR / "embedding_ids.json"

BATCH_SIZE = 100
RPM_LIMIT = 100
MIN_INTERVAL = 60.0 / RPM_LIMIT
DIM = 4096
BASE_URL = "https://api.upstage.ai/v1/solar"
MAX_CHARS = 12000  # ~3000 tokens, safely under 4000 token limit
MAX_RETRIES = 3


def _get_api_keys() -> list[str]:
    """Collect all UPSTAGE_API_KEY* from env."""
    keys = []
    for i in range(1, 100):
        key = os.getenv(f"UPSTAGE_API_KEY{i}")
        if key:
            keys.append(key.strip())
        else:
            break
    if not keys:
        single = os.getenv("UPSTAGE_API_KEY", "")
        if single:
            keys.append(single.strip())
    return keys


def _truncate(text: str) -> str:
    """Truncate text to stay within token limits."""
    if len(text) > MAX_CHARS:
        return text[:MAX_CHARS]
    return text


def _embed_batch_safe(client: OpenAI, batch: list[str]) -> list[list[float]]:
    """Embed a batch with retry and fallback to smaller sub-batches."""
    truncated = [_truncate(t) for t in batch]

    for attempt in range(MAX_RETRIES):
        try:
            response = client.embeddings.create(
                model="solar-embedding-1-large-passage",
                input=truncated,
            )
            sorted_data = sorted(response.data, key=lambda x: x.index)
            return [item.embedding for item in sorted_data]
        except Exception as e:
            err_msg = str(e)
            if "maximum context length" in err_msg or "4000 tokens" in err_msg:
                # Split batch in half and process separately
                mid = len(truncated) // 2
                if mid == 0:
                    # Single text too long, truncate more aggressively
                    truncated = [t[:MAX_CHARS // 2] for t in truncated]
                    continue
                left = _embed_batch_safe(client, truncated[:mid])
                time.sleep(MIN_INTERVAL)
                right = _embed_batch_safe(client, truncated[mid:])
                return left + right
            elif attempt < MAX_RETRIES - 1:
                wait = 2 ** (attempt + 1)
                time.sleep(wait)
            else:
                raise


def embed_passages(texts: list[str], ids: list[str], progress_callback=None) -> np.ndarray:
    """Embed passages using parallel API keys.

    Args:
        texts: List of passage strings to embed.
        ids: List of document IDs (same length as texts).
        progress_callback: Optional callback(current, total) for progress updates.

    Returns:
        np.ndarray of shape (N, 4096), dtype float32.

    Hints:
        - Use _get_api_keys() to get API keys, OpenAI(api_key=..., base_url=BASE_URL) to create clients
        - Use _embed_batch_safe(client, batch) to embed a batch of texts
        - Process texts in chunks of BATCH_SIZE
        - Save results to EMBEDDINGS_PATH (.npy) and IDS_PATH (.json)
    """
    if len(texts) != len(ids):
        raise ValueError("texts and ids must be the same length")

    api_keys = _get_api_keys()
    if not api_keys:
        raise ValueError("No UPSTAGE_API_KEY found in environment.")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize result array
    embeddings = np.zeros((len(ids), DIM), dtype=np.float32)
    done_ids: set[str] = set()

    cached = load_cached_embeddings()
    if cached is not None:
        cached_embs, cached_ids = cached
        if (
            len(cached_ids) == len(ids)
            and cached_embs.shape == (len(ids), DIM)
            and cached_ids == ids
        ):
            return cached_embs

        id_to_idx = {doc_id: i for i, doc_id in enumerate(ids)}
        for j, doc_id in enumerate(cached_ids):
            idx = id_to_idx.get(doc_id)
            if idx is None or j >= cached_embs.shape[0]:
                continue
            embeddings[idx] = cached_embs[j]
            done_ids.add(doc_id)

    remaining_indices = [i for i, doc_id in enumerate(ids) if doc_id not in done_ids]
    if not remaining_indices:
        np.save(EMBEDDINGS_PATH, embeddings.astype(np.float32))
        IDS_PATH.write_text(json.dumps(ids, ensure_ascii=False))
        return embeddings

    batches = [
        remaining_indices[i:i + BATCH_SIZE]
        for i in range(0, len(remaining_indices), BATCH_SIZE)
    ]
    total_batches = len(batches)
    lock = Lock()
    next_batch_idx = 0
    completed_batches = 0

    def _save_partial():
        completed_indices = [i for i, doc_id in enumerate(ids) if doc_id in done_ids]
        if not completed_indices:
            return
        emb = embeddings[completed_indices].astype(np.float32)
        id_list = [ids[i] for i in completed_indices]
        np.save(EMBEDDINGS_PATH, emb)
        IDS_PATH.write_text(json.dumps(id_list, ensure_ascii=False))

    def _worker(client: OpenAI):
        nonlocal next_batch_idx, completed_batches
        last_call = 0.0
        while True:
            with lock:
                if next_batch_idx >= total_batches:
                    return
                batch_indices = batches[next_batch_idx]
                next_batch_idx += 1

            # Enforce per-key rate limit
            elapsed = time.time() - last_call
            if elapsed < MIN_INTERVAL:
                time.sleep(MIN_INTERVAL - elapsed)

            batch_texts = [texts[i] for i in batch_indices]
            batch_embeddings = _embed_batch_safe(client, batch_texts)
            last_call = time.time()

            with lock:
                for idx, emb in zip(batch_indices, batch_embeddings):
                    embeddings[idx] = np.array(emb, dtype=np.float32)
                    done_ids.add(ids[idx])

                completed_batches += 1
                _save_partial()

    clients = [OpenAI(api_key=k, base_url=BASE_URL) for k in api_keys]
    with ThreadPoolExecutor(max_workers=len(clients)) as executor:
        futures = [executor.submit(_worker, client) for client in clients]
        if progress_callback:
            last_reported = -1
            while True:
                done, not_done = wait(futures, timeout=0.2)
                with lock:
                    current = completed_batches
                if current != last_reported:
                    progress_callback(current, total_batches)
                    last_reported = current
                if not not_done:
                    break
        for f in as_completed(futures):
            f.result()

    # Save final full embeddings aligned to ids
    np.save(EMBEDDINGS_PATH, embeddings.astype(np.float32))
    IDS_PATH.write_text(json.dumps(ids, ensure_ascii=False))
    return embeddings


def embed_query(query: str) -> list[float]:
    """Embed a single query using the query model.

    Args:
        query: The search query string.

    Returns:
        list[float] of length 4096 (embedding vector).

    Hints:
        - Use _get_api_keys() to get an API key
        - Model name: "solar-embedding-1-large-query"
        - Use _truncate() to handle long queries
    """
    api_keys = _get_api_keys()
    if not api_keys:
        raise ValueError("No UPSTAGE_API_KEY found in environment.")
    client = OpenAI(api_key=api_keys[0], base_url=BASE_URL)
    response = client.embeddings.create(
        model="solar-embedding-1-large-query",
        input=_truncate(query),
    )
    return response.data[0].embedding


def load_cached_embeddings() -> tuple[np.ndarray, list[str]] | None:
    """Load cached embeddings from disk. Returns (embeddings, ids) or None."""
    if EMBEDDINGS_PATH.exists() and IDS_PATH.exists():
        embeddings = np.load(EMBEDDINGS_PATH)
        ids = json.loads(IDS_PATH.read_text())
        return embeddings, ids
    return None


if __name__ == "__main__":
    from data.download import RAW_DIR

    corpus_path = RAW_DIR / "corpus.jsonl"
    if not corpus_path.exists():
        print("Run data/download.py first.")
        raise SystemExit(1)

    texts, ids = [], []
    with open(corpus_path, encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            ids.append(doc["id"])
            texts.append(doc["text"])

    embed_passages(texts, ids)
