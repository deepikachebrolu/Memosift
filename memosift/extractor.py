"""Memory extraction layer.

Two providers:
- GemmaProvider: calls Gemma via the Gemini API (GEMINI_API_KEY + optional
  GEMINI_MODEL, defaults to a Gemma open-weight model id).
- RuleBasedProvider: offline, deterministic fallback so the demo always runs.

Output memory record schema (kept stable across providers):

{
  "id": str, "summary": str, "layer": "semantic"|"episodic",
  "facts": [{"key": str, "value": str}],
  "original_text": str
}
"""

import json
import re
import uuid

FACT_PATTERNS = {
    "person": r"\b(?:met|talked to|spoke with|call(?:ed)?|emailed)\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)",
    "topic": r"\b(?:learning|studying|building|recommends?|reco(?:mmend)?)\s+(?:learning\s+)?([a-zA-Z+\-\s#\[\]]{3,40})",
    "location": r"\bin\s+((?:Hyderabad|Bengaluru|Bangalore|Delhi|Mumbai|Chennai|Pune|India))",
    "deadline": r"\b(?:deadline|due|by)\s+(October\s+\d{1,2},?\s+20\d{2}|tomorrow|next week)",
    "tool": r"\b(Qiskit|Cirq|Gemma|LangChain|LlamaIndex|vLLM|FAISS|Chroma)\b",
}


class RuleBasedProvider:
    """Deterministic fallback extractor: regex-based fact spotting + compression."""

    name = "rule-based"

    def extract(self, text: str) -> list[dict]:
        facts = {}
        for key, pat in FACT_PATTERNS.items():
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                facts[key] = m.group(1).strip().rstrip(".")
        # summary: compact fact-based line when facts exist; fallback to
        # truncated first sentences otherwise
        if facts:
            summary = "; ".join(f"{k}: {v}" for k, v in facts.items())
        else:
            sentences = re.split(r"(?<=[.!?])\s+", text.strip())
            summary = " ".join(sentences[:2])[:160]
        return [
            {
                "id": uuid.uuid4().hex[:8],
                "summary": summary,
                "layer": "semantic" if facts else "episodic",
                "facts": [{"key": k, "value": v} for k, v in facts.items()],
                "original_text": text,
            }
        ]


class GemmaProvider:
    """Calls Gemma through the Gemini API for structured memory extraction."""

    name = "gemma"

    def __init__(self, api_key: str, model: str = "gemma-3-27b-it"):
        self.api_key = api_key
        self.model = model
        self._prompt = (
            "You are a memory extraction engine. From the text below, output ONLY "
            "valid JSON: {\"summary\": str (<=40 words), \"layer\": \"semantic\" if it "
            "contains durable facts else \"episodic\", \"facts\": [ {\"key\": one of "
            "person|topic|location|deadline|tool|preference, \"value\": str} ] } \n\nTEXT:\n"
        )

    def extract(self, text: str) -> list[dict]:
        try:
            from google import genai  # lazy import

            client = genai.Client(api_key=self.api_key)
            resp = client.models.generate_content(
                model=self.model, contents=self._prompt + text
            )
            data = json.loads(
                re.search(r"\{.*\}", resp.text, re.DOTALL).group(0)
            )
            data.setdefault("layer", "episodic")
            data["id"] = uuid.uuid4().hex[:8]
            data["original_text"] = text
            data["facts"] = [
                {"key": f.get("key", "note"), "value": f.get("value", "")}
                for f in data.get("facts", [])
                if isinstance(f, dict)
            ]
            return [data]
        except Exception as e:  # degrade gracefully to rules
            fb = RuleBasedProvider().extract(text)
            for m in fb:
                m["provider_fallback_reason"] = str(e)[:120]
            return fb


def get_provider():
    import os

    key = os.getenv("GEMINI_API_KEY")
    if key:
        return GemmaProvider(key, os.getenv("GEMINI_MODEL", "gemma-3-27b-it"))
    return RuleBasedProvider()
def extract_memories(text: str) -> dict:
    sentences = [
        sentence.strip()
        for sentence in re.split(r"[.!?]\s+", text)
        if sentence.strip()
    ]

    topics = []
    topic_words = [
        "python",
        "ai",
        "blockchain",
        "quantum",
        "project",
        "memory",
        "token",
        "hackathon",
    ]

    lower_text = text.lower()

    for word in topic_words:
        if word in lower_text:
            topics.append(word)

    return {
        "summary": " ".join(sentences[:3])[:500],
        "facts": sentences[:10],
        "entities": [],
        "topics": topics,
    }
