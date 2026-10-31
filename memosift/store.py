import re
import uuid


class MemoryStore:
    def __init__(self):
        self.memories = {}

    def add(self, memory: dict) -> str:
        new_text = self._normalized_text(
            memory.get("compressed_text", "")
        )

        for memory_id, existing in self.memories.items():
            existing_text = self._normalized_text(
                existing.get("compressed_text", "")
            )

            if new_text and new_text == existing_text:
                memory["id"] = memory_id
                self.memories[memory_id] = {
                    **existing,
                    **memory,
                }
                return memory_id

        memory_id = str(uuid.uuid4())

        self.memories[memory_id] = {
            **memory,
            "id": memory_id,
        }

        return memory_id

    def get(self, memory_id: str):
        return self.memories.get(memory_id)

    def all(self):
        return list(self.memories.values())

    def search(self, query: str, token_budget: int = 500):
        query_terms = set(
            re.findall(r"\w+", query.lower())
        )

        ranked = []

        for memory in self.memories.values():
            text = (
                memory.get("compressed_text", "")
                + " "
                + memory.get("original_text", "")
            ).lower()

            score = sum(
                1
                for term in query_terms
                if term in text
            )

            if score > 0:
                ranked.append((score, memory))

        ranked.sort(
            key=lambda item: (
                item[0],
                item[1].get("importance_score", 0),
            ),
            reverse=True,
        )

        results = []
        used_tokens = 0
        seen = set()

        for _, memory in ranked:
            normalized = self._normalized_text(
                memory.get("compressed_text", "")
            )

            if normalized in seen:
                continue

            memory_tokens = memory.get(
                "compressed_tokens",
                0,
            )

            if used_tokens + memory_tokens > token_budget:
                continue

            results.append(memory)
            used_tokens += memory_tokens
            seen.add(normalized)

        return results

    @staticmethod
    def _normalized_text(text: str) -> str:
        return " ".join(
            text.lower().split()
        )
