---
paths:
  - "tests/**/*.py"
---

# Test inputs

Use example domains, dummy tokens, and small synthetic responses. Mock the transport before exercising anything that could send an HTTP request. Assert the method, endpoint, headers, and payload where those details are part of the contract.
