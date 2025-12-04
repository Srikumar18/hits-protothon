"""
Standalone summarization utilities.

Provides:
  - try_load_abstractive(): attempts to load an abstractive HF pipeline (DistilBART) with retries.
  - get_summarizer(): returns the pipeline if available.
  - summarize_text(): main entrypoint (abstractive if available, else extractive fallback).
  - extractive_summarize(): deterministic offline extractive summarizer.

Environment variables:
  - LOCAL_SUMMARY_MODEL: path to a locally-downloaded HF model folder (optional)
  - FORCE_EXTRACTIVE_SUMMARY: if "1"/"true"/"yes" -> always use extractive fallback
"""
import os
import time
import math
import heapq
import re
from typing import Optional

# transformers is optional; if missing we fall back to extractive summarizer only.
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
except Exception:
    pipeline = None
    AutoTokenizer = None
    AutoModelForSeq2SeqLM = None

# Minimal stopword list for extractive fallback
_STOPWORDS = {
    "the","and","is","in","it","of","to","a","for","on","that","this","with",
    "as","are","was","be","by","or","an","from","at","has","have","which","we",
    "can","not","but","will","their","they","its","these","such","also"
}

SUMMARIZER = None
SUMMARIZER_AVAILABLE = False

def try_load_abstractive(model_name: str = "sshleifer/distilbart-cnn-12-6",
                         max_attempts: int = 3,
                         backoff_factor: float = 1.5) -> Optional[object]:
    """
    Try to load a Hugging Face summarization pipeline. Returns pipeline or None.
    Retries with exponential backoff. If LOCAL_SUMMARY_MODEL env var is set,
    attempts to load locally (local_files_only=True).
    """
    global SUMMARIZER_AVAILABLE, SUMMARIZER

    if pipeline is None:
        # transformers not installed — can't load abstractive model
        SUMMARIZER_AVAILABLE = False
        return None

    attempt = 0
    last_exc = None

    while attempt < max_attempts:
        attempt += 1
        try:
            local_model = os.getenv("LOCAL_SUMMARY_MODEL", "").strip()
            if local_model:
                # Load from local files only (no network)
                tokenizer = AutoTokenizer.from_pretrained(local_model, local_files_only=True)
                model = AutoModelForSeq2SeqLM.from_pretrained(local_model, local_files_only=True)
                pipe = pipeline("summarization", model=model, tokenizer=tokenizer)
            else:
                # Remote load (will attempt to download/cache).
                # If your environment has no internet, this will raise and we fall back.
                pipe = pipeline("summarization", model=model_name)
            SUMMARIZER_AVAILABLE = True
            SUMMARIZER = pipe
            return pipe
        except Exception as e:
            last_exc = e
            wait = backoff_factor ** attempt
            print(f"[extract.summarizer] load attempt {attempt} failed: {e}. Retrying in {wait:.1f}s...")
            time.sleep(wait)

    SUMMARIZER_AVAILABLE = False
    print(f"[extract.summarizer] failed to load abstractive model after {max_attempts} attempts. Last error: {last_exc}")
    return None


# Replace get_summarizer and summarize_text with these versions:

def get_summarizer(force_reload: bool = False, max_attempts: int = 3) -> Optional[object]:
    """
    Returns the loaded summarization pipeline if available.
    If force_reload=True, attempts to load the abstractive model now (may block).
    max_attempts controls how many tries are used when force_reload=True.
    """
    global SUMMARIZER
    if SUMMARIZER is not None and not force_reload:
        return SUMMARIZER

    # Only attempt to load if explicitly asked for (force_reload) or if a local model is configured
    local_model = os.getenv("LOCAL_SUMMARY_MODEL", "").strip()
    if not force_reload and not local_model:
        # Do NOT block: user didn't request load and no local model set — return None immediately
        return SUMMARIZER

    # If we reach here, attempt to load (this can block). Use try_load_abstractive with fewer attempts.
    try:
        SUMMARIZER = try_load_abstractive(max_attempts=max_attempts)
    except Exception as e:
        print(f"[extract.summarizer] get_summarizer load error: {e}")
        SUMMARIZER = None
    return SUMMARIZER


def summarize_text(text: str,
                   max_chunk_chars: int = 1200,
                   min_length: int = 50,
                   max_length: int = 200,
                   abstractive: bool = True,
                   try_load_abstractive_now: bool = False) -> str:
    """
    Primary summarization entry point.

    By default this function returns a fast extractive summary **unless**:
      - FORCE_EXTRACTIVE_SUMMARY env var is set, or
      - an abstractive pipeline is already loaded (SUMMARIZER is not None), or
      - the caller passes try_load_abstractive_now=True (this will attempt to load, and may block).

    Parameters:
      - try_load_abstractive_now: when True, attempt to load the HF model immediately (may block).
    """
    if not text or not text.strip():
        return ""

    # Explicit force to use extractive fallback
    if os.getenv("FORCE_EXTRACTIVE_SUMMARY", "").lower() in ("1", "true", "yes"):
        return extractive_summarize(text, max_sentences=5)

    # If abstractive not requested at all, use extractive fast path
    if not abstractive:
        return extractive_summarize(text, max_sentences=5)

    # If summarizer already loaded, use it
    if SUMMARIZER is not None and SUMMARIZER_AVAILABLE:
        pipe = SUMMARIZER
    else:
        # If the caller asked to attempt load now, try a short load; otherwise use extractive fallback.
        if try_load_abstractive_now:
            # Try a quick load with fewer attempts
            pipe = get_summarizer(force_reload=True, max_attempts=1)
            # If still None, fallback
            if pipe is None:
                return extractive_summarize(text, max_sentences=6)
        else:
            # Do not block — return extractive summary immediately
            return extractive_summarize(text, max_sentences=6)

    # At this point `pipe` is available and we can perform abstractive summarization
    sentences = _tokenize_sentences(text)
    chunks = []
    cur = ""
    for s in sentences:
        if len(cur) + len(s) + 1 <= max_chunk_chars:
            cur = (cur + " " + s).strip()
        else:
            if cur:
                chunks.append(cur)
            cur = s
    if cur:
        chunks.append(cur)

    chunk_summaries = []
    for chunk in chunks:
        try:
            out = pipe(chunk, max_length=max_length, min_length=min_length, do_sample=False, truncation=True)
            if isinstance(out, list) and out:
                chunk_summaries.append(out[0].get('summary_text', '').strip())
            else:
                chunk_summaries.append(extractive_summarize(chunk, max_sentences=2))
        except Exception as e:
            print(f"[extract.summarizer] abstractive summarization failed for chunk: {e}")
            chunk_summaries.append(extractive_summarize(chunk, max_sentences=2))

    combined = " ".join([s for s in chunk_summaries if s]).strip()

    if pipe and len(combined) > max_chunk_chars:
        try:
            final = pipe(combined, max_length=max_length, min_length=max(int(min_length/2), 10), do_sample=False, truncation=True)
            if isinstance(final, list) and final:
                combined = final[0].get('summary_text', combined).strip()
        except Exception as e:
            print(f"[extract.summarizer] final condense failed: {e}")

    return combined or extractive_summarize(text, max_sentences=6)



# ---- Extractive fallback summarizer ----

def _tokenize_sentences(text: str):
    """Simple sentence tokenizer using punctuation heuristics."""
    sentences = re.split(r'(?<=[\.\?\!])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def _score_sentences_by_freq(text: str):
    """
    Build a normalized word frequency table (excluding stopwords) and score each sentence
    by the sum of the frequencies of words it contains (normalized by sentence length).
    """
    words = re.findall(r'\w+', text.lower())
    freq = {}
    for w in words:
        if w in _STOPWORDS or len(w) <= 2:
            continue
        freq[w] = freq.get(w, 0) + 1
    if not freq:
        return {}
    maxf = max(freq.values())
    for k in freq:
        freq[k] = freq[k] / maxf

    sentences = _tokenize_sentences(text)
    scores = {}
    for s in sentences:
        s_words = re.findall(r'\w+', s.lower())
        score = 0.0
        for w in s_words:
            if w in freq:
                score += freq[w]
        # normalize by log(length) to reduce long-sentence bias
        scores[s] = score / (math.log(len(s_words) + 1) + 1)
    return scores


def extractive_summarize(text: str, max_sentences: int = 5) -> str:
    """
    Simple extractive summarizer:
      - Scores sentences by word-frequency importance.
      - Returns top-scoring sentences in the original document order.
    Deterministic and works offline (no dependencies beyond stdlib).
    """
    if not text or not text.strip():
        return ""
    sentences = _tokenize_sentences(text)
    if len(sentences) <= max_sentences:
        return " ".join(sentences)
    scores = _score_sentences_by_freq(text)
    if not scores:
        # fallback: return the first N sentences
        return " ".join(sentences[:max_sentences])
    top_n = heapq.nlargest(max_sentences, scores.items(), key=lambda kv: kv[1])
    top_set = set([kv[0] for kv in top_n])
    # preserve original order
    ordered = [s for s in sentences if s in top_set]
    # If we selected fewer (due to duplicates), pad with leading sentences
    if len(ordered) < max_sentences:
        for s in sentences:
            if s not in top_set:
                ordered.append(s)
            if len(ordered) >= max_sentences:
                break
    return " ".join(ordered[:max_sentences])

# Public API
__all__ = [
    "try_load_abstractive",
    "get_summarizer",
    "summarize_text",
    "extractive_summarize",
]

