# Margin Notes

Margin Notes is a synchronous Python SDK and CLI for checking model discovery and inference across gateways.

- `margin_notes/__init__.py` owns the HTTP client and its public interface.
- `margin_notes/__main__.py` parses CLI arguments and prints JSON.
- `tests/test_client.py` checks the wire contract with a mocked transport.
- `.env.example` lists the environment variables for the SDK.

The main development loop is `python3 -m unittest discover -s tests` followed by `python3 -m margin_notes --help`. Use the exact gateway model ID in examples and keep provider-specific setup in local overrides. Use `/check-sdk` for a repeatable offline check and `/review-wire-contract` when editing request construction.
