# MemoSift 

**Token-efficient, verifiable memory layer for AI agents.**

MemoSift turns long conversations into compact structured memories, retrieves only
what is needed under a token budget, and proves that memories are untouched with a
SHA-256 hash-chain ledger (blockchain-ready).

Built for [Hacktoberfest Hack Day Hyderabad x AI Community Hyderabad](https://www.mlh.com/events/hacktoberfest-hack-day-hyderabad-x-ai-community-hyderabad) — Oct 31, 2026.

## Quick start

```bash
# offline demo (no API key needed)
python3 demo.py

# with tests
python3 -m pytest tests/ -v
```

## Use Gemma (Best Use of Gemma 4 prize)

```bash
export GEMINI_API_KEY="your-key"
export GEMINI_MODEL="gemma-3-27b-it"   # any open-weight Gemma model id
python3 demo.py
```

The extractor falls back to a deterministic rule-based provider when no key is
set, so the demo is always runnable.

## How it works

```
conversation ──▶ extractor (Gemma / rules) ──▶ memory record
                                                   │
                              ┌────────────────────┼─────────────────────┐
                              ▼                    ▼                     ▼
                       semantic layer        episodic layer         hash ledger
                       (compact facts)       (compressed summary)   (SHA-256 chain)
                              │                    │                     │
                              └───────┬────────────┘                     │
                                      ▼                                  │
                        token-budget retrieval (greedy relevance/token)   │
                                      ▼                                  │
                              compressed prompt ◀──── integrity check ◀──┘
```

## Project structure

```
memosift/
├── memosift/
│   ├── __init__.py     # package
│   ├── extractor.py    # Gemma + rule-based extraction
│   ├── integrity.py    # SHA-256 hash-chain ledger
│   ├── store.py        # layered memory + token-budget retrieval
│   └── tokens.py       # token counting (tiktoken or fallback)
├── tests/test_memosift.py
├── demo.py             # end-to-end offline demo
└── README.md
```

## Key features for judges

| Feature | What it shows |
|---|---|
| Token budget retrieval | Retrieves under 300 tokens instead of replaying full history |
| Compression % | Measured before/after on real conversations |
| Integrity ledger | Tamper detection after showing the "chain valid" flow |
| Gemma integration | Real structured extraction + screenshot-ready demo output |
| Offline fallback | Demo never breaks during judging |

## Next steps for the hackathon day
- Add Streamlit front-end (one page: paste transcript → see token savings + memory cards)
- Record a real chain deployment (e.g. a testnet smart contract storing hashes)
- Add screenshot ingestion (Gemma multimodal) for pasted error/wiki images
- Optional quantum-inspired ranking: small Cirq circuit vs greedy baseline
