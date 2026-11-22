"""Command-line entry point for trying individual inference requests."""

import argparse
import json
import sys

from . import DEFAULT_TIMEOUT, Client, InferenceError


def main(argv=None):
    parser = argparse.ArgumentParser(description="Try model discovery and inference against a configurable gateway.")
    parser.add_argument(
        "--timeout", type=float, default=DEFAULT_TIMEOUT,
        help="HTTP socket timeout in seconds (default: %(default)s)",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("models", help="List available models as JSON")
    for name, protocol in (("chat", "OpenAI Chat Completions"), ("messages", "Anthropic Messages")):
        command = commands.add_parser(name, help=f"Send one {protocol} request")
        command.add_argument("--model", required=True, help="Exact model ID from the model list")
        command.add_argument("--max-tokens", type=int, default=128)
        command.add_argument("prompt")
    args = parser.parse_args(argv)
    if args.command != "models" and args.max_tokens < 1:
        parser.error("--max-tokens must be positive.")

    try:
        client = Client(timeout=args.timeout)
        if args.command == "models":
            result = client.list_models()
        else:
            send = client.chat if args.command == "chat" else client.messages
            result = send(args.model, [{"role": "user", "content": args.prompt}], max_tokens=args.max_tokens)
    except (InferenceError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
