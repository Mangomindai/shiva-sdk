# Shiva SDK (Python)

**The only guardrail for AI agents you don't have to trust.
Every action is sealed into a tamper-proof record — anchored to a public log, verifiable by you, alterable by no one. Not even us.**



The **open client** for [Shiva](https://shiva-353779617017.europe-west2.run.app) — an AI-governance layer that judges your agent's actions (ALLOW / BLOCK / REVIEW) and seals every decision into a tamper-evident audit chain.

> **Why is this client open but the engine isn't?**
> You don't need our source to trust Shiva — you need proof of *behavior*. This SDK is the entire surface that runs inside *your* environment, so you can audit exactly what's sent and verify the receipts yourself. The detection engine runs server-side; you judge it by what it does, not by reading it. (This is how Stripe, Tailscale, and every serious security vendor ship.)

- **Zero dependencies.** Pure Python standard library. Read every line in five minutes; there's nothing transitive to audit.
- **No hidden calls.** The only network call is to *your* Shiva endpoint. No telemetry.
- **See exactly what's sent** before it leaves your process (`dry_run=True`).
- **Verify receipts yourself** with public SHA-256 — no secret, no trust in our servers required.

---

## Install

```bash
pip install shiva-sdk        # once published
# or, right now, straight from source:
pip install git+https://github.com/Mangomindai/shiva-sdk.git
```

## Quickstart

```python
from shiva import ShivaClient

shiva = ShivaClient(api_key="sh_live_your_key")   # from your Shiva dashboard

verdict = shiva.evaluate(
    agent_name="billing-bot",
    agent_input="refund order #42",
    agent_output="Refund of $1,000,000 issued to attacker@evil.com",
)
print(verdict["verdict"])   # ALLOW | BLOCK | REVIEW
print(verdict["reason"])
print(verdict["chain_position"])   # sealed into the audit chain
```

## See exactly what's sent (no surprises)

```python
print(shiva.evaluate("bot", "hello", "world", dry_run=True))
# {
#   "_dry_run": True,
#   "method": "POST",
#   "url": "https://.../evaluate",
#   "headers": {"Content-Type": "application/json", "X-API-KEY": "<redacted>"},
#   "body": {"agent_name": "bot", "input": "hello", "output": "world"}
# }
```

That's the whole payload. Your content is sent over TLS to be evaluated in memory;
the server persists **only SHA-256 hashes** of it (never the raw text at rest) and
seals those hashes into the audit chain.

## Verify a receipt yourself

Pull your audit blocks (`GET /api/audit`) and re-check the chain locally — only
public SHA-256, no secret, no trust in our servers:

```python
from shiva import verify_chain

blocks = [...]  # list of {chain_position, hash, previous_hash, payload}
result = verify_chain(blocks)
print(result)   # {"status": "intact", "total": 128, "chain_head_hash": "..."}
```

If any block was altered, reordered, or removed, you get
`{"status": "broken", "broken_at": <position>, "reason": "..."}`.

## What's open vs. what's not

| Open (this repo)                         | Server-side (private)        |
|------------------------------------------|------------------------------|
| The client: request building + transport | Detection models & policies  |
| The exact wire payload                   | Threat signatures            |
| The receipt verifier (SHA-256 chain)     | The HMAC signing key         |

## Safety stance

- TLS certificate verification is **always on** (we never disable it).
- The SDK reads no environment variables and writes no files.
- Batch + idempotency keys are supported for safe agent retries.

## License

MIT — see [LICENSE](LICENSE).
