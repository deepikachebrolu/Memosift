"""SHA-256 integrity ledger for memories.

Stores only hashes (never content), simulating what would be written to a
blockchain / distributed ledger. Swap `LocalLedger.record` with a smart
contract call for a real chain demo.
"""

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict


@dataclass
class LedgerEntry:
    memory_id: str
    content_hash: str
    timestamp: float
    prev_hash: str = "GENESIS"


@dataclass
class IntegrityLedger:
    def __init__(self):
        self.records = {}

    def hash_content(self, memory_id: str, content: str) -> str:
        raw = f"{memory_id}:{content}".encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def record(self, memory_id: str, content: str) -> str:
        digest = self.hash_content(memory_id, content)
        self.records[memory_id] = digest
        return digest

    def verify(self, memory_id: str, content: str) -> bool:
        current = self.hash_content(memory_id, content)
        return self.records.get(memory_id) == current