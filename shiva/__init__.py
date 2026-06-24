"""Shiva SDK — the open client for the Shiva AI-governance API.

Zero dependencies (Python stdlib only). The whole client is two short files:
  - client.py  : builds + sends the request (the entire network surface)
  - verify.py  : independently verifies a tamper-evident audit receipt
"""
from .client import ShivaClient, ShivaError
from .verify import verify_chain, canonical_payload

__version__ = "0.1.0"
__all__ = ["ShivaClient", "ShivaError", "verify_chain", "canonical_payload"]
