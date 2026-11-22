import io
import json
import os
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from margin_notes import InferenceError, Client
from margin_notes.__main__ import main

MESSAGES = [{"role": "user", "content": "Hello"}]


class ClientTest(unittest.TestCase):
    def setUp(self):
        self.client = Client("mock-token", base_url="https://gateway.example.invalid/v1")
        opener = patch.object(self.client._opener, "open")
        self.open = opener.start()
        self.addCleanup(opener.stop)

    def test_environment_configuration(self):
        env = {"INFERENCE_API_KEY": "mock-token", "INFERENCE_BASE_URL": "https://gateway.example.invalid/v1/"}
        with patch.dict(os.environ, env, clear=True):
            self.assertEqual(Client().base_url, "https://gateway.example.invalid/v1")

    def test_base_url_is_required(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "Set INFERENCE_BASE_URL"):
                Client("mock-token")

    def test_model_discovery(self):
        listing = {"data": [{"id": "demo-model"}]}
        self.open.return_value = io.BytesIO(json.dumps(listing).encode())
        self.assertEqual(self.client.list_models(), listing)
        request = self.open.call_args.args[0]
        self.assertEqual(request.get_method(), "GET")
        self.assertTrue(request.full_url.endswith("/v1/models"))
        self.assertEqual(request.get_header("Authorization"), "Bearer mock-token")
        self.assertEqual(self.open.call_args.kwargs["timeout"], 30.0)

    def test_cli_passes_timeout_to_client(self):
        with patch("margin_notes.__main__.Client") as client, patch("sys.stdout", new_callable=io.StringIO):
            client.return_value.list_models.return_value = {"data": []}
            self.assertEqual(main(["--timeout", "2.5", "models"]), 0)
            client.assert_called_once_with(timeout=2.5)

    def test_invalid_timeouts(self):
        for timeout in (0, -1, float("inf"), float("nan")):
            with self.subTest(timeout=timeout), self.assertRaisesRegex(ValueError, "Request timeout"):
                Client("mock-token", base_url="https://gateway.example.invalid/v1", timeout=timeout)

    def test_chat_completion(self):
        self.open.return_value = io.BytesIO(b'{"choices":[]}')
        self.client.chat("demo-model", MESSAGES, max_tokens=12)
        request = self.open.call_args.args[0]
        self.assertTrue(request.full_url.endswith("/v1/chat/completions"))
        self.assertEqual(request.get_header("Authorization"), "Bearer mock-token")
        self.assertEqual(json.loads(request.data), {
            "model": "demo-model", "messages": MESSAGES, "max_tokens": 12,
        })

    def test_anthropic_messages(self):
        self.open.return_value = io.BytesIO(b'{"content":[]}')
        self.client.messages("demo-model", MESSAGES, system="Be brief.")
        request = self.open.call_args.args[0]
        self.assertTrue(request.full_url.endswith("/v1/messages"))
        headers = {name.lower(): value for name, value in request.header_items()}
        self.assertEqual(headers["x-api-key"], "mock-token")
        self.assertEqual(headers["anthropic-version"], "2023-06-01")
        self.assertNotIn("authorization", headers)
        self.assertEqual(json.loads(request.data)["system"], "Be brief.")

    def test_http_error_omits_response_body(self):
        self.open.side_effect = HTTPError(
            "https://gateway.example.invalid/v1/models", 429, "Limited", {}, io.BytesIO(b"private data"),
        )
        with self.assertRaisesRegex(InferenceError, r"^Inference API returned HTTP 429 for /models\.$"):
            self.client.list_models()

    def test_unexpected_response(self):
        self.open.return_value = io.BytesIO(b'[]')
        with self.assertRaisesRegex(InferenceError, "Expected a JSON object"):
            self.client.list_models()


if __name__ == "__main__":
    unittest.main()
