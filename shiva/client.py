"""
shiva.client — the open client for the Shiva governance API.

This file is the ENTIRE network surface of the SDK. Read it top to bottom: it
builds a JSON payload, POSTs it over HTTPS to your Shiva endpoint, and returns
the verdict. There is no telemetry, no hidden call, and no third-party
dependency — Python standard library only.

Trust hook: `evaluate(..., dry_run=True)` returns the EXACT request (url, headers,
body) that *would* be sent, without sending anything — so you can audit precisely
what leaves your process before it ever does.
"""
from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.request

# Your deployed Shiva endpoint. Override per-client with base_url=...
DEFAULT_BASE_URL = "https://shiva-353779617017.europe-west2.run.app"


class ShivaError(Exception):
    """Raised on a transport failure or a non-2xx API response."""

    def __init__(self, message: str, status: int | None = None, body=None):
        super().__init__(message)
        self.status = status
        self.body = body


class ShivaClient:
    """A thin, auditable client around the Shiva `/evaluate` API.

    >>> shiva = ShivaClient(api_key="sh_live_...")
    >>> verdict = shiva.evaluate("billing-bot", "refund order 42", "done")
    >>> verdict["verdict"]   # ALLOW | BLOCK | REVIEW
    """

    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL, timeout: float = 15.0):
        if not api_key:
            raise ValueError("api_key is required (get one from your Shiva dashboard)")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    # — payload construction: this is exactly, and only, what gets sent —
    @staticmethod
    def build_payload(agent_name: str, agent_input: str, agent_output: str,
                      idempotency_key: str | None = None) -> dict:
        payload = {
            "agent_name": agent_name,
            "input": agent_input,
            "output": agent_output,
        }
        if idempotency_key:
            payload["idempotency_key"] = idempotency_key
        return payload

    def evaluate(self, agent_name: str, agent_input: str, agent_output: str,
                 idempotency_key: str | None = None, dry_run: bool = False) -> dict:
        """Evaluate one agent action; returns the verdict dict.

        dry_run=True returns the exact request that WOULD be sent (with the API
        key redacted) and sends nothing — audit what leaves your process.
        """
        payload = self.build_payload(agent_name, agent_input, agent_output, idempotency_key)
        if dry_run:
            return {
                "_dry_run": True,
                "method": "POST",
                "url": f"{self.base_url}/evaluate",
                "headers": {"Content-Type": "application/json", "X-API-KEY": "<redacted>"},
                "body": payload,
            }
        return self._post("/evaluate", payload)

    def evaluate_batch(self, items) -> dict:
        """Evaluate several actions in one request.
        items: iterable of {agent_name, input, output[, idempotency_key]}."""
        return self._post("/evaluate/batch", {"items": list(items)})

    # — the single point where data leaves your process —
    def _post(self, path: str, body: dict) -> dict:
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}{path}",
            data=data,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "X-API-KEY": self.api_key,
                "User-Agent": "shiva-sdk-python/0.1",
            },
        )
        # Always verify TLS. We never disable certificate checking.
        ctx = ssl.create_default_context()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=ctx) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", "replace")
            try:
                parsed = json.loads(raw)
            except Exception:
                parsed = raw
            raise ShivaError(f"Shiva API error {e.code}", status=e.code, body=parsed)
        except urllib.error.URLError as e:
            raise ShivaError(f"Could not reach Shiva at {self.base_url}: {e.reason}")
