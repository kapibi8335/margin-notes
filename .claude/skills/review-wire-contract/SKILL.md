---
name: review-wire-contract
description: Review a change to request construction and response handling.
disable-model-invocation: true
---

Read the diff for the client, CLI, and transport tests. Check that the versioned base URL is joined once, authentication matches each protocol, and the CLI keeps JSON and diagnostics on their expected streams.

Run the offline tests and report concrete findings with file and line references.
