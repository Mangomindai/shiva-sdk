"""
shiva.verify — independently verify a Shiva audit receipt.

Shiva seals every decision into a hash chain: each block's hash commits to the
previous block's hash plus the (content-minimized) payload. This module lets YOU
recompute that chain from receipts you collected — using only public SHA-256,
with no secret key and no trust in Shiva's servers. If a single block was
altered, reordered, or removed, verification fails loudly.

What this proves: the chain is internally consistent and append-only — i.e.
tamper-evident. What it does NOT check: the HMAC signature on each block (that
needs the server's secret key). For that, call POST /api/audit/verify, which
re-verifies signatures server-side.

This is the whole point of the design: you don't have to trust our code to trust
the receipt — cryptography does the work, and the cryptography is right here.
"""
from __future__ import annotations

import hashlib
import json

# Matches the server's genesis anchor (models.py).
GENESIS = hashlib.sha256(b"GENESIS").hexdigest()


def canonical_payload(block: dict) -> str:
    """The exact string a block's hash commits to. Mirrors the server byte-for-
    byte: prefer the stored canonical `payload_text`; for legacy blocks without
    it, re-dump `payload` with sorted keys and compact separators.

    Do not 'tidy' these json.dumps args — they must match the server's seal.
    """
    pt = block.get("payload_text")
    if pt is not None:
        return pt
    return json.dumps(block["payload"], sort_keys=True, separators=(",", ":"))


def verify_chain(blocks: list[dict]) -> dict:
    """Verify audit blocks (any order; sorted here by chain_position ascending).

    Each block needs: chain_position, hash, previous_hash, and either
    payload_text or payload. Returns one of:
        {"status": "intact",  "total": N, "chain_head_hash": "..."}
        {"status": "broken",  "broken_at": pos, "reason": "..."}
        {"status": "empty",   "total": 0}
    """
    if not blocks:
        return {"status": "empty", "total": 0}

    expected_prev = GENESIS
    for block in sorted(blocks, key=lambda b: b["chain_position"]):
        payload_str = canonical_payload(block)
        expected_hash = hashlib.sha256(
            f"{block['previous_hash']}{payload_str}".encode()
        ).hexdigest()

        if block["previous_hash"] != expected_prev:
            return {"status": "broken", "broken_at": block["chain_position"],
                    "reason": "previous_hash does not link to the prior block (reorder/deletion)"}
        if block["hash"] != expected_hash:
            return {"status": "broken", "broken_at": block["chain_position"],
                    "reason": "hash mismatch — the sealed payload was altered"}
        expected_prev = block["hash"]

    return {"status": "intact", "total": len(blocks), "chain_head_hash": expected_prev}
