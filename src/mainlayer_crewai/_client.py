"""Mainlayer HTTP client — shared request logic for all tools."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

import httpx

DEFAULT_BASE_URL = "https://api.mainlayer.fr"
DEFAULT_TIMEOUT = 30


class MainlayerClient:
    """Thin synchronous HTTP client for the Mainlayer API.

    All tools share one client instance per toolkit to reuse connection pools.
    """

    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a GET request and return the parsed JSON body.

        Returns a dict with an ``"error"`` key on failure rather than raising,
        so tools can surface clean error strings to the LLM.
        """
        try:
            with httpx.Client(timeout=DEFAULT_TIMEOUT) as client:
                response = client.get(
                    f"{self.base_url}{path}",
                    params=params,
                    headers=self._headers,
                )
                response.raise_for_status()
                return response.json()  # type: ignore[return-value]
        except httpx.HTTPStatusError as exc:
            return {"error": f"HTTP {exc.response.status_code}: {exc.response.text}"}
        except httpx.RequestError as exc:
            return {"error": f"Request failed: {exc}"}

    def post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a POST request with a JSON body and return the parsed JSON body."""
        try:
            with httpx.Client(timeout=DEFAULT_TIMEOUT) as client:
                response = client.post(
                    f"{self.base_url}{path}",
                    json=payload,
                    headers=self._headers,
                )
                response.raise_for_status()
                return response.json()  # type: ignore[return-value]
        except httpx.HTTPStatusError as exc:
            return {"error": f"HTTP {exc.response.status_code}: {exc.response.text}"}
        except httpx.RequestError as exc:
            return {"error": f"Request failed: {exc}"}

    @staticmethod
    def format(data: Any) -> str:
        """Serialize data to a pretty-printed JSON string for tool output."""
        return json.dumps(data, indent=2)
