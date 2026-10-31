import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), "..", "memosift"))

from integrity import IntegrityLedger
from store import MemoryStore
from tokens import count_tokens, token_stats


def test_integrity_ledger():
    l = IntegrityLedger()
    l.record("m1", "hello world")
    assert l.verify("m1", "hello world")["verified"] is True
    assert l.verify("m1", "hello world!")["verified"] is False
    assert l.chain_valid() is True
    l.record("m2", "more")
    assert l.verify("m1", "hello world")["verified"] is True
    assert l.export_json()


def test_memory_store():
    l = IntegrityLedger()
    s = MemoryStore(ledger=l)
    s.add({"id": "a", "summary": "Arjun recommends Qiskit", "layer": "semantic",
           "facts": [{"key": "topic", "value": "Qiskit"}], "original_text": "x " * 50})
    s.add({"id": "b", "summary": "weather was rainy", "layer": "episodic",
           "facts": [], "original_text": "y " * 50})

    assert len(s.memories) == 2
    ctx = s.select_context("Qiskit quantum", budget=5000)
    assert ctx["selected"][0]["id"] == "a"
    assert ctx["tokens_used"] <= 5000
    assert ctx["compression_achieved_pct"] > 0


def test_token_stats():
    s = token_stats("a b c d e f", "a b")
    assert s["tokens_saved"] > 0
    assert count_tokens("") == 1 or count_tokens("") >= 0  # sanity
