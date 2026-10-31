import re


IMPORTANT_PATTERNS = [
    r"\b\d{1,4}[/-]\d{1,2}[/-]\d{1,4}\b",
    r"\b\d{4}\b",
    r"\bdeadline\b",
    r"\bmeeting\b",
    r"\bdecision\b",
    r"\bpreference\b",
    r"\bimportant\b",
    r"\bproject\b",
    r"\bgoal\b",
    r"\btask\b",
    r"\bpassword\b",
    r"\bapi key\b",
    r"\btoken\b",
]


def score_memory(text: str) -> dict:
    clean_text = text.strip()

    if not clean_text:
        return {
            "importance_score": 0,
            "confidence": 0,
            "signals": [],
        }

    lowered = clean_text.lower()
    signals = []

    for pattern in IMPORTANT_PATTERNS:
        if re.search(pattern, lowered):
            signals.append(pattern.replace(r"\b", ""))

    sentences = [
        item.strip()
        for item in re.split(r"[.!?]\s+", clean_text)
        if item.strip()
    ]

    length_score = min(len(clean_text) / 500, 1.0)
    signal_score = min(len(signals) / 5, 1.0)
    sentence_score = min(len(sentences) / 8, 1.0)

    importance = round(
        (
            length_score * 0.25
            + signal_score * 0.55
            + sentence_score * 0.20
        )
        * 100
    )

    confidence = round(
        min(
            100,
            50
            + len(signals) * 8
            + min(len(sentences), 5) * 4,
        )
    )

    return {
        "importance_score": importance,
        "confidence": confidence,
        "signals": signals,
    }
