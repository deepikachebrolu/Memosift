import json
from pathlib import Path
from threading import Lock


class JsonMemoryDatabase:
    def __init__(self, path: str = "data/memories.json"):
        self.path = Path(path)
        self.lock = Lock()

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not self.path.exists():
            self.path.write_text(
                "[]",
                encoding="utf-8",
            )

    def read(self):
        with self.lock:
            return json.loads(
                self.path.read_text(encoding="utf-8")
            )

    def write(self, memories):
        with self.lock:
            self.path.write_text(
                json.dumps(
                    memories,
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
