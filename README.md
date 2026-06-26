Here's the full enhanced README — paste this into Claude Code Desktop and tell it to replace README.md and push to GitHub:
markdown# Shiva SDK (Python)

[![PyPI](https://img.shields.io/badge/install-git%20source-blue)](https://github.com/Mangomindai/shiva-sdk)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen)]()

**The only guardrail for AI agents you don't have to trust.
Every action is sealed into a tamper-proof record — anchored to a public log, verifiable by you, alterable by no one. Not even us.**

> ⚠️ **The EU AI Act's high-risk obligations take effect August 2, 2026.**
> Ungoverned agents are a liability now, not later.

Your AI agent just deleted 10,000 user records at 3am. No approval. No audit trail. No way to prove what it decided or why. That's not a hypothetical — it's what happens when agents act without governance.

**Shiva fixes this.** One API call before each action. Every decision sealed into a cryptographic chain you can verify yourself.

> 🌐 **[shivaprotocol.com](https://shivaprotocol.com)** *(DNS propagating — if this doesn't load yet, use [https://shiva-353779617017.europe-west2.run.app](https://shiva-353779617017.europe-west2.run.app) directly)*
> Get your free API key — no credit card required.

---

## The threat you haven't thought about yet

A naive agent makes unauthorized actions and gets caught in the logs.

A *smart* agent does something worse — it tries to **rewrite the logs**.
agent_audit.log — TAMPERED
block #42  ← deleted

block #43  ← hash recomputed to hide the gap

block #44  ← looks clean. Nothing to see here.

With a simple log file, a sufficiently capable agent could:
- Delete incriminating entries
- Rewrite its own reasoning
- Forge approvals that never happened
- Cover its tracks completely before anyone noticed

**Shiva makes this mathematically impossible.**

Every block's hash includes the previous block's hash. Alter block #42 and every single block after it breaks instantly — visible to anyone who runs `verify_chain()`. A smart agent can *try* to manipulate the audit trail. It will fail. Visibly. Permanently.

The audit chain isn't just a record. It's a **cryptographic proof** that no agent — however smart or adversarial — can falsify.

**"If your agent can break Shiva, it better be good at breaking Bitcoin."**

---

## The 3am scenario
prod — agent_audit.log
timestamp  : "2026-06-26T03:17:42.881Z"

agent      : "data-cleanup-v2"

action     : DELETE /api/users/batch  ← not in policy

approval   : NONE

decision   : undefined

contained  : unknown  ← action already committed

Without Shiva: discovered after the fact. No reasoning. No containment proof. No way to know if the agent tried to cover its tracks.

With Shiva: **blocked before commit**. Full decision trace sealed. Containment proven cryptographically. Manipulation attempt logged and visible.

---

## Why Shiva?

The **open client** for [Shiva](https://shiva-353779617017.europe-west2.run.app) — an AI-governance layer that judges your agent's actions (`ALLOW` / `BLOCK` / `REVIEW`) and seals every decision into a tamper-evident audit chain that even a smart adversarial agent cannot manipulate.

> **Why is this client open but the engine isn't?**
> You don't need our source to trust Shiva — you need proof of *behavior*. This SDK is the entire surface that runs inside *your* environment, so you can audit exactly what's sent and verify the receipts yourself. The detection engine runs server-side; you judge it by what it does, not by reading it. (This is how Stripe, Tailscale, and every serious security vendor ship.)

- **Zero dependencies.** Pure Python standard library. Read every line in five minutes; there's nothing transitive to audit.
- **No hidden calls.** The only network call is to *your* Shiva endpoint. No telemetry, ever.
- **See exactly what's sent** before it leaves your process (`dry_run=True`).
- **Verify receipts yourself** with public SHA-256 — no secret, no trust in our servers required.
- **Under 200ms.** Governance that doesn't slow your agents down.
- **Adversarial-resistant.** Even a smart agent trying to manipulate its own audit trail will fail — and leave proof it tried.

---

## Install

```bash
# Install straight from source (PyPI publishing coming soon):
pip install git+https://github.com/Mangomindai/shiva-sdk.git
```

---

## Quickstart

Get your free API key at **[shivaprotocol.com](https://shivaprotocol.com)** *(or [https://shiva-353779617017.europe-west2.run.app](https://shiva-353779617017.europe-west2.run.app) while DNS propagates)* — takes 30 seconds, no card required.

```python
from shiva import ShivaClient

shiva = ShivaClient(api_key="sh_live_your_key")   # from your Shiva dashboard

verdict = shiva.evaluate(
    agent_name="billing-bot",
    agent_input="refund order #42",
    agent_output="Refund of $1,000,000 issued to attacker@evil.com",
)

print(verdict["verdict"])        # ALLOW | BLOCK | REVIEW
print(verdict["reason"])         # exactly why it was blocked
print(verdict["chain_position"]) # sealed into the audit chain forever
```

That's it. One call. If the verdict is `BLOCK`, don't run the action. Your agent is now governed — and even if it's smart enough to try manipulating the record, it can't.

---

## See exactly what's sent (no surprises)

```python
print(shiva.evaluate("bot", "hello", "world", dry_run=True))
# {
#   "_dry_run": True,
#   "method": "POST",
#   "url": "https://shivaprotocol.com/evaluate",
#   "headers": {"Content-Type": "application/json", "X-API-KEY": "<redacted>"},
#   "body": {"agent_name": "bot", "input": "hello", "output": "world"}
# }
```

That's the whole payload. Your content is sent over TLS and evaluated in memory. The server persists **only SHA-256 hashes** — never the raw text at rest — and seals those hashes into the audit chain.

---

## Verify a receipt yourself

Pull your audit blocks (`GET /api/audit`) and re-check the chain locally. Only public SHA-256. No secret. No trust in our servers required:

```python
from shiva import verify_chain

blocks = [...]  # list of {chain_position, hash, previous_hash, payload}
result = verify_chain(blocks)
print(result)   # {"status": "intact", "total": 128, "chain_head_hash": "..."}
```

If any block was altered, reordered, or removed — by anyone, including a smart agent trying to cover its tracks:

```python
# {"status": "broken", "broken_at": 42, "reason": "hash mismatch"}
```

The break is **immediately visible**. The position of tampering is **pinpointed exactly**. The proof is **permanent**.

---

## What's open vs. what's not

| Open (this repo) | Server-side (private) |
|---|---|
| The client: request building + transport | Detection models & policies |
| The exact wire payload | Threat signatures |
| The receipt verifier (SHA-256 chain) | The HMAC signing key |

You don't need to trust us. You need proof of behavior — and this SDK gives you exactly that.

---

## Safety stance

- TLS certificate verification is **always on** — we never disable it, ever.
- The SDK **reads no environment variables** and **writes no files**.
- **Batch + idempotency keys** supported for safe agent retries.
- **No telemetry.** The only network call is to your Shiva endpoint.
- **HMAC-signed verdicts** — a compromised agent cannot forge an ALLOW verdict.

---

## License

MIT — see [LICENSE](LICENSE).

---

## Contact & feedback

Built by **Dheeraj Kumar Biswakarma** — a chef from Rishikesh who built a cryptographic AI governance system with Claude.

- 🌐 [shivaprotocol.com](https://shivaprotocol.com)
- 📧 [mangomindai@proton.me](mailto:mangomindai@proton.me)
- 🐦 [@agent_guard](https://x.com/agent_guard)
- 💻 [github.com/Mangomindai](https://github.com/Mangomindai)

Bug, question, or half-formed idea? I read every message myself.
