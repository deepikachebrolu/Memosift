"""Token counting utilities.

Uses tiktoken when available; falls back to a whitespace heuristic so the
demo always works offline.
"""

try:
    import tiktoken

    _enc = tiktoken.get_encoding("cl100k_base")

    def count_tokens(text: str) -> int:
        return len(_enc.encode(text))

except Exception:  # pragma: no cover - offline fallback

    def count_tokens(text: str) -> int:
        # crude approximation: ~1.3 tokens per whitespace-separated word
        return max(1, int(len(text.split()) * 1.3))


def token_stats(original: str, compressed: str) -> dict:
    o, c = count_tokens(original), count_tokens(compressed)
    saved = o - c
    pct = (saved / o * 100) if o else 0.0
    return {
        "original_tokens": o,
        "compressed_tokens": c,
        "tokens_saved": saved,
        "saved_percent": round(pct, 1),
    }
