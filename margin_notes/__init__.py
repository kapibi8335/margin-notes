"""Small synchronous client for inference gateways."""

import json
import math
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

DEFAULT_TIMEOUT = 30.0


class InferenceError(Exception):
    """The API request failed or returned an invalid response."""


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Client:
    """Call model discovery and non-streaming inference endpoints."""

    def __init__(self, api_key=None, *, base_url=None, timeout=DEFAULT_TIMEOUT):
        self._api_key = api_key if api_key is not None else os.getenv("INFERENCE_API_KEY")
        if not self._api_key:
            raise ValueError("Set INFERENCE_API_KEY or pass api_key.")
        configured_url = base_url or os.getenv("INFERENCE_BASE_URL")
        if not configured_url:
            raise ValueError("Set INFERENCE_BASE_URL or pass base_url.")
        self.base_url = configured_url.rstrip("/")
        url = urlsplit(self.base_url)
        if (url.scheme != "https" or not url.hostname or url.username is not None
                or url.query or url.fragment):
            raise ValueError("INFERENCE_BASE_URL must be an HTTPS URL without credentials, query, or fragment.")
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("Request timeout must be a finite positive number of seconds.")
        self.timeout = timeout
        self._opener = build_opener(_NoRedirect())

    def list_models(self):
        """Return the model listing, including the IDs in data."""
        return self._request("/models")

    def chat(self, model, messages, *, max_tokens=128):
        """Send an OpenAI-style chat completion and return the JSON response."""
        return self._request("/chat/completions", {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
        })

    def messages(self, model, messages, *, max_tokens=128, system=None):
        """Send an Anthropic-style Messages request and return the JSON response."""
        payload = {"model": model, "messages": messages, "max_tokens": max_tokens}
        if system is not None:
            payload["system"] = system
        return self._request("/messages", payload, anthropic=True)

    def _request(self, path, payload=None, *, anthropic=False):
        headers = {"Accept": "application/json"}
        if anthropic:
            headers.update({"x-api-key": self._api_key, "anthropic-version": "2023-06-01"})
        else:
            headers["Authorization"] = f"Bearer {self._api_key}"

        data = None
        if payload is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(payload).encode("utf-8")
        request = Request(self.base_url + path, data=data, headers=headers)

        try:
            with self._opener.open(request, timeout=self.timeout) as response:
                body = json.load(response)
        except HTTPError as error:
            error.close()
            raise InferenceError(f"Inference API returned HTTP {error.code} for {path}.") from None
        except (URLError, TimeoutError):
            raise InferenceError(f"Could not reach the inference API for {path}.") from None
        except (ValueError, UnicodeError):
            raise InferenceError(f"Expected JSON from {path}.") from None

        if not isinstance(body, dict):
            raise InferenceError(f"Expected a JSON object from {path}.")
        return body
