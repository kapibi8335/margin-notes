---
paths:
  - "margin_notes/__init__.py"
  - "tests/test_client.py"
---

# HTTP contract

Use Bearer authentication for model discovery and Chat Completions. Messages uses the API key header and the Anthropic version header. Append endpoint paths to the configured versioned URL.

Keep HTTP failures actionable with the status code and request path. Treat response bodies as potentially sensitive.
