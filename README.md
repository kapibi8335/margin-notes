# Margin Notes

Margin Notes is a Python SDK and CLI for inspecting inference gateways. It supports model discovery, OpenAI-compatible Chat Completions, and Anthropic-compatible Messages. It requires Python 3.10 or later and uses only the standard library at runtime.

## CLI

Set `INFERENCE_BASE_URL` and `INFERENCE_API_KEY` in the process environment. The base URL should include the version prefix used by your gateway, such as `/v1`. See `.env.example` for the expected names.

```sh
python3 -m margin_notes --help
python3 -m margin_notes models
python3 -m margin_notes --timeout 5 models
python3 -m margin_notes chat --model MODEL_ID --max-tokens 64 "Give an example of a haiku."
python3 -m margin_notes messages --model MODEL_ID --max-tokens 64 "Give an example of a limerick."
```

Use an exact model ID returned by `models`. Inference commands print API responses as JSON. The HTTP socket timeout defaults to 30 seconds. Set `--timeout` before the subcommand to use a different value. Install with `python3 -m pip install .` to use the `margin-notes` entry point.

## Python

```python
from margin_notes import Client

client = Client()
models = client.list_models()
model = models["data"][0]["id"]
reply = client.chat(
    model,
    [{"role": "user", "content": "What is a limerick?"}],
    max_tokens=64,
)
print(reply["choices"][0]["message"]["content"])
```

The client accepts explicit `base_url`, `api_key`, and `timeout` arguments. HTTP and response errors raise `InferenceError` without printing response bodies.

## Development

Run `python3 -m unittest discover -s tests` for mocked HTTP tests. The Claude Code project instructions describe the test and review workflows. The local settings example shows how to specify a gateway for a development session. [Claude Code project settings](https://code.claude.com/docs/en/settings)
