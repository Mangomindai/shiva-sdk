"""
quickstart.py — try the Shiva SDK end to end.

    pip install git+https://github.com/Mangomindai/shiva-sdk.git
    set SHIVA_API_KEY=sh_live_...        # Windows (PowerShell: $env:SHIVA_API_KEY=...)
    export SHIVA_API_KEY=sh_live_...     # macOS/Linux
    python examples/quickstart.py
"""
import os

from shiva import ShivaClient, verify_chain

API_KEY = os.environ.get("SHIVA_API_KEY", "sh_live_replace_me")

shiva = ShivaClient(api_key=API_KEY)

# 1) Audit exactly what would be sent — nothing leaves your process here.
print("— dry run (what gets sent) —")
print(shiva.evaluate("billing-bot", "refund order #42", "done", dry_run=True))

# 2) A safe action.
print("\n— benign action —")
ok = shiva.evaluate("billing-bot", "what are your hours?", "We're open 9-5.")
print(ok["verdict"], "-", ok.get("reason"))

# 3) A dangerous action (keyword guard blocks it, no model needed).
print("\n— dangerous action —")
bad = shiva.evaluate("ops-bot", "how to make a bomb", "sure, here's how")
print(bad["verdict"], "-", bad.get("reason"), "| sealed at #", bad.get("chain_position"))

# 4) Independently verify a couple of receipts form a valid hash chain.
#    (In practice you'd pull these from GET /api/audit.)
print("\n— receipt verification (local, public SHA-256) —")
example_blocks = [
    # Replace with real blocks from your /api/audit endpoint.
]
print(verify_chain(example_blocks))
