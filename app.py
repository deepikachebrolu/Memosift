from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from memosift.extractor import extract_memories
from memosift.integrity import IntegrityLedger
from memosift.store import MemoryStore
from memosift.tokens import count_tokens
from memosift.config import settings
from memosift.scoring import score_memory


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(
    title="MemoSift",
    description="A token-efficient and verifiable memory layer for AI applications.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/static",
    StaticFiles(directory=str(FRONTEND_DIR)),
    name="static",
)

store = MemoryStore()
ledger = IntegrityLedger()


class MemoryRequest(BaseModel):
    text: str
    compression_level: str = "balanced"


class QueryRequest(BaseModel):
    query: str
    token_budget: int = 500


@app.get("/")
def serve_frontend():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.post("/api/memories")
def create_memory(payload: MemoryRequest):
    text = payload.text.strip()

    if not text:
        raise HTTPException(
            status_code=400,
            detail="Please enter a memory or conversation.",
        )

    original_tokens = count_tokens(text)

    try:
        extracted = extract_memories(text)
    except Exception:
        extracted = {
            "summary": text[:500],
            "facts": [],
            "entities": [],
            "topics": [],
        }

    if isinstance(extracted, dict):
        summary = extracted.get("summary") or text[:500]
        facts = extracted.get("facts", [])
        entities = extracted.get("entities", [])
        topics = extracted.get("topics", [])
    else:
        summary = str(extracted)
        facts = []
        entities = []
        topics = []

    compressed_memory = build_compressed_memory(
        summary=summary,
        facts=facts,
        entities=entities,
        topics=topics,
        compression_level=payload.compression_level,
    )

    compressed_tokens = count_tokens(compressed_memory)
    tokens_saved = max(original_tokens - compressed_tokens, 0)
    savings_percent = (
        round((tokens_saved / original_tokens) * 100, 1)
        if original_tokens
        else 0
    )
    scoring = score_memory(text)
    memory = {
        "original_text": text,
        "summary": summary,
        "facts": facts,
        "entities": entities,
        "topics": topics,
        "compressed_text": compressed_memory,
        "original_tokens": original_tokens,
        "compressed_tokens": compressed_tokens,
        "tokens_saved": tokens_saved,
        "savings_percent": savings_percent,
        "compression_level": payload.compression_level,
        "importance_score": scoring["importance_score"],
        "confidence": scoring["confidence"],
        "signals": scoring["signals"],
    }

    memory_id = store.add(memory)
    memory["id"] = memory_id

    memory_hash = ledger.record(memory_id, compressed_memory)
    memory["hash"] = memory_hash

    return {
        "memory": memory,
        "stats": {
            "original_tokens": original_tokens,
            "compressed_tokens": compressed_tokens,
            "tokens_saved": tokens_saved,
            "savings_percent": savings_percent,
        },
    }


@app.post("/api/query")
def query_memories(payload: QueryRequest):
    query = payload.query.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Please enter a question.",
        )

    memories = store.search(
        query=query,
        token_budget=payload.token_budget,
    )

    selected_text = "\n\n".join(
        memory.get("compressed_text", "")
        for memory in memories
    )

    return {
        "query": query,
        "answer_context": selected_text,
        "memories": memories,
        "tokens_used": count_tokens(selected_text),
        "token_budget": payload.token_budget,
    }


@app.get("/api/memories")
def list_memories():
    memories = store.all()
    return {
        "memories": memories,
        "count": len(memories),
    }


@app.post("/api/verify/{memory_id}")
def verify_memory(memory_id: str):
    memory = store.get(memory_id)

    if not memory:
        raise HTTPException(
            status_code=404,
            detail="Memory not found.",
        )

    current_hash = ledger.hash_content(
        memory_id,
        memory.get("compressed_text", ""),
    )

    stored_hash = memory.get("hash")

    return {
        "memory_id": memory_id,
        "verified": current_hash == stored_hash,
        "stored_hash": stored_hash,
        "current_hash": current_hash,
    }
@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "environment": settings.app_env,
        "model_configured": bool(settings.gemini_api_key),
    }


def build_compressed_memory(
    summary,
    facts,
    entities,
    topics,
    compression_level,
):
    lines = [
        f"Summary: {summary}",
    ]

    if entities:
        lines.append(
            "Entities: " + ", ".join(map(str, entities[:12]))
        )

    if topics:
        lines.append(
            "Topics: " + ", ".join(map(str, topics[:12]))
        )

    if facts:
        if compression_level == "aggressive":
            facts = facts[:5]
        elif compression_level == "balanced":
            facts = facts[:10]

        lines.append(
            "Facts: " + " | ".join(map(str, facts))
        )

    return "\n".join(lines)

@app.get("/api/analytics")
def analytics():
    memories = store.all()

    if not memories:
        return {
            "memory_count": 0,
            "original_tokens": 0,
            "compressed_tokens": 0,
            "tokens_saved": 0,
            "savings_percent": 0,
            "average_importance": 0,
        }

    original_tokens = sum(
        memory.get("original_tokens", 0)
        for memory in memories
    )

    compressed_tokens = sum(
        memory.get("compressed_tokens", 0)
        for memory in memories
    )

    tokens_saved = max(
        original_tokens - compressed_tokens,
        0,
    )

    average_importance = round(
        sum(
            memory.get("importance_score", 0)
            for memory in memories
        )
        / len(memories)
    )

    savings_percent = round(
        (tokens_saved / original_tokens) * 100,
        1,
    ) if original_tokens else 0

    return {
        "memory_count": len(memories),
        "original_tokens": original_tokens,
        "compressed_tokens": compressed_tokens,
        "tokens_saved": tokens_saved,
        "savings_percent": savings_percent,
        "average_importance": average_importance,
    }
