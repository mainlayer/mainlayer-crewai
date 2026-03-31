"""Tests for Mainlayer CrewAI tools using mocked HTTP."""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from mainlayer_crewai import (
    CheckAccessTool,
    CreateResourceTool,
    DiscoverResourcesTool,
    GetResourceInfoTool,
    MainlayerToolkit,
    PayForResourceTool,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

API_KEY = "ml_test_key"
WALLET = "0xdeadbeef"
BASE_URL = "https://api.mainlayer.xyz"

SAMPLE_RESOURCES = [
    {
        "id": "res_weather_001",
        "name": "OpenWeather Pro",
        "description": "Real-time weather data API",
        "type": "api",
        "fee_model": "pay_per_call",
        "price": 0.01,
    },
    {
        "id": "res_news_002",
        "name": "Global News Feed",
        "description": "Aggregated news from 500+ sources",
        "type": "api",
        "fee_model": "subscription",
        "price": 9.99,
    },
]

SAMPLE_RESOURCE_DETAIL = {
    "id": "res_weather_001",
    "name": "OpenWeather Pro",
    "description": "Real-time weather data API with 1-minute resolution",
    "type": "api",
    "fee_model": "pay_per_call",
    "price": 0.01,
    "endpoint_url": "https://api.openweather.example.com/v1",
    "status": "active",
}

SAMPLE_PAYMENT = {
    "transaction_id": "txn_abc123",
    "resource_id": "res_weather_001",
    "payer_wallet": WALLET,
    "amount": 0.01,
    "status": "confirmed",
    "access_token": "tok_xyz789",
}

SAMPLE_ENTITLEMENT = {
    "has_access": True,
    "resource_id": "res_weather_001",
    "payer_wallet": WALLET,
    "expires_at": "2027-12-31T23:59:59Z",
    "remaining_credits": 99,
}

SAMPLE_ENTITLEMENT_NO_ACCESS = {
    "has_access": False,
    "resource_id": "res_weather_001",
    "payer_wallet": WALLET,
}

SAMPLE_CREATED_RESOURCE = {
    "id": "res_my_api_003",
    "name": "My Sentiment API",
    "description": "Real-time text sentiment analysis",
    "type": "api",
    "fee_model": "pay_per_call",
    "price": 0.005,
    "status": "active",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_client_get(data: Any) -> MagicMock:
    """Patch MainlayerClient.get to return data."""
    mock = MagicMock(return_value=data)
    return mock


def _mock_client_post(data: Any) -> MagicMock:
    """Patch MainlayerClient.post to return data."""
    mock = MagicMock(return_value=data)
    return mock


# ---------------------------------------------------------------------------
# DiscoverResourcesTool
# ---------------------------------------------------------------------------


class TestDiscoverResourcesTool:
    def _make_tool(self) -> DiscoverResourcesTool:
        return DiscoverResourcesTool(api_key=API_KEY, base_url=BASE_URL)

    def test_name(self) -> None:
        tool = self._make_tool()
        assert tool.name == "discover_mainlayer_resources"

    def test_description_mentions_mainlayer(self) -> None:
        tool = self._make_tool()
        assert "Mainlayer" in tool.description

    def test_description_mentions_resource_id(self) -> None:
        """Description should guide agents toward the next step."""
        tool = self._make_tool()
        assert "resource_id" in tool.description

    def test_run_returns_resource_list(self) -> None:
        tool = self._make_tool()
        with patch(
            "mainlayer_crewai.tools.discover.MainlayerClient.get",
            return_value=SAMPLE_RESOURCES,
        ):
            result = tool._run(query="weather")

        parsed = json.loads(result)
        assert isinstance(parsed, list)
        assert parsed[0]["id"] == "res_weather_001"

    def test_run_with_type_and_fee_model_filters(self) -> None:
        tool = self._make_tool()
        captured_params: dict = {}

        def mock_get(path: str, params: dict = None) -> Any:  # type: ignore[assignment]
            captured_params.update(params or {})
            return SAMPLE_RESOURCES

        with patch("mainlayer_crewai.tools.discover.MainlayerClient.get", side_effect=mock_get):
            tool._run(query="weather", type="api", fee_model="pay_per_call", limit=5)

        assert captured_params["type"] == "api"
        assert captured_params["fee_model"] == "pay_per_call"
        assert captured_params["limit"] == 5

    def test_run_omits_blank_type_filter(self) -> None:
        tool = self._make_tool()
        captured_params: dict = {}

        def mock_get(path: str, params: dict = None) -> Any:  # type: ignore[assignment]
            captured_params.update(params or {})
            return SAMPLE_RESOURCES

        with patch("mainlayer_crewai.tools.discover.MainlayerClient.get", side_effect=mock_get):
            tool._run(query="news", type="", fee_model="")

        assert "type" not in captured_params
        assert "fee_model" not in captured_params

    def test_run_returns_error_string_on_api_error(self) -> None:
        tool = self._make_tool()
        with patch(
            "mainlayer_crewai.tools.discover.MainlayerClient.get",
            return_value={"error": "HTTP 401: Unauthorized"},
        ):
            result = tool._run(query="weather")

        parsed = json.loads(result)
        assert "error" in parsed

    def test_run_handles_wrapped_response(self) -> None:
        """API may return {resources: [...]} instead of a bare list."""
        tool = self._make_tool()
        wrapped = {"resources": SAMPLE_RESOURCES, "total": 2}
        with patch(
            "mainlayer_crewai.tools.discover.MainlayerClient.get",
            return_value=wrapped,
        ):
            result = tool._run(query="weather")

        parsed = json.loads(result)
        assert isinstance(parsed, list)
        assert len(parsed) == 2


# ---------------------------------------------------------------------------
# GetResourceInfoTool
# ---------------------------------------------------------------------------


class TestGetResourceInfoTool:
    def _make_tool(self) -> GetResourceInfoTool:
        return GetResourceInfoTool(api_key=API_KEY, base_url=BASE_URL)

    def test_name(self) -> None:
        tool = self._make_tool()
        assert tool.name == "get_mainlayer_resource_info"

    def test_description_mentions_resource_id(self) -> None:
        tool = self._make_tool()
        assert "resource_id" in tool.description

    def test_run_returns_resource_detail(self) -> None:
        tool = self._make_tool()
        with patch(
            "mainlayer_crewai.tools.get_info.MainlayerClient.get",
            return_value=SAMPLE_RESOURCE_DETAIL,
        ):
            result = tool._run(resource_id="res_weather_001")

        parsed = json.loads(result)
        assert parsed["id"] == "res_weather_001"
        assert parsed["status"] == "active"

    def test_run_calls_correct_endpoint(self) -> None:
        tool = self._make_tool()
        captured_path: list = []

        def mock_get(path: str, params: dict = None) -> Any:  # type: ignore[assignment]
            captured_path.append(path)
            return SAMPLE_RESOURCE_DETAIL

        with patch("mainlayer_crewai.tools.get_info.MainlayerClient.get", side_effect=mock_get):
            tool._run(resource_id="res_weather_001")

        assert captured_path[0] == "/resources/public/res_weather_001"


# ---------------------------------------------------------------------------
# PayForResourceTool
# ---------------------------------------------------------------------------


class TestPayForResourceTool:
    def _make_tool(self) -> PayForResourceTool:
        return PayForResourceTool(api_key=API_KEY, base_url=BASE_URL)

    def test_name(self) -> None:
        tool = self._make_tool()
        assert tool.name == "pay_for_mainlayer_resource"

    def test_description_mentions_pay(self) -> None:
        tool = self._make_tool()
        assert "pay" in tool.description.lower()

    def test_description_advises_check_first(self) -> None:
        tool = self._make_tool()
        assert "check" in tool.description.lower()

    def test_run_returns_payment_confirmation(self) -> None:
        tool = self._make_tool()
        with patch(
            "mainlayer_crewai.tools.pay.MainlayerClient.post",
            return_value=SAMPLE_PAYMENT,
        ):
            result = tool._run(resource_id="res_weather_001", payer_wallet=WALLET)

        parsed = json.loads(result)
        assert parsed["status"] == "confirmed"
        assert parsed["transaction_id"] == "txn_abc123"

    def test_run_sends_correct_payload(self) -> None:
        tool = self._make_tool()
        captured_payload: dict = {}

        def mock_post(path: str, payload: dict) -> Any:
            captured_payload.update(payload)
            return SAMPLE_PAYMENT

        with patch("mainlayer_crewai.tools.pay.MainlayerClient.post", side_effect=mock_post):
            tool._run(resource_id="res_weather_001", payer_wallet=WALLET)

        assert captured_payload["resource_id"] == "res_weather_001"
        assert captured_payload["payer_wallet"] == WALLET

    def test_run_calls_pay_endpoint(self) -> None:
        tool = self._make_tool()
        captured_path: list = []

        def mock_post(path: str, payload: dict) -> Any:
            captured_path.append(path)
            return SAMPLE_PAYMENT

        with patch("mainlayer_crewai.tools.pay.MainlayerClient.post", side_effect=mock_post):
            tool._run(resource_id="res_weather_001", payer_wallet=WALLET)

        assert captured_path[0] == "/pay"


# ---------------------------------------------------------------------------
# CheckAccessTool
# ---------------------------------------------------------------------------


class TestCheckAccessTool:
    def _make_tool(self) -> CheckAccessTool:
        return CheckAccessTool(api_key=API_KEY, base_url=BASE_URL)

    def test_name(self) -> None:
        tool = self._make_tool()
        assert tool.name == "check_mainlayer_access"

    def test_description_mentions_access(self) -> None:
        tool = self._make_tool()
        assert "access" in tool.description.lower()

    def test_description_advises_before_pay(self) -> None:
        tool = self._make_tool()
        assert "pay_for_mainlayer_resource" in tool.description

    def test_run_returns_access_granted(self) -> None:
        tool = self._make_tool()
        with patch(
            "mainlayer_crewai.tools.check_access.MainlayerClient.get",
            return_value=SAMPLE_ENTITLEMENT,
        ):
            result = tool._run(resource_id="res_weather_001", payer_wallet=WALLET)

        parsed = json.loads(result)
        assert parsed["has_access"] is True
        assert parsed["remaining_credits"] == 99

    def test_run_returns_access_denied(self) -> None:
        tool = self._make_tool()
        with patch(
            "mainlayer_crewai.tools.check_access.MainlayerClient.get",
            return_value=SAMPLE_ENTITLEMENT_NO_ACCESS,
        ):
            result = tool._run(resource_id="res_weather_001", payer_wallet=WALLET)

        parsed = json.loads(result)
        assert parsed["has_access"] is False

    def test_run_sends_correct_params(self) -> None:
        tool = self._make_tool()
        captured_params: dict = {}

        def mock_get(path: str, params: dict = None) -> Any:  # type: ignore[assignment]
            captured_params.update(params or {})
            return SAMPLE_ENTITLEMENT

        with patch(
            "mainlayer_crewai.tools.check_access.MainlayerClient.get",
            side_effect=mock_get,
        ):
            tool._run(resource_id="res_weather_001", payer_wallet=WALLET)

        assert captured_params["resource_id"] == "res_weather_001"
        assert captured_params["payer_wallet"] == WALLET


# ---------------------------------------------------------------------------
# CreateResourceTool
# ---------------------------------------------------------------------------


class TestCreateResourceTool:
    def _make_tool(self) -> CreateResourceTool:
        return CreateResourceTool(api_key=API_KEY, base_url=BASE_URL)

    def test_name(self) -> None:
        tool = self._make_tool()
        assert tool.name == "create_mainlayer_resource"

    def test_description_mentions_create(self) -> None:
        tool = self._make_tool()
        assert "create" in tool.description.lower()

    def test_run_creates_resource(self) -> None:
        tool = self._make_tool()
        with patch(
            "mainlayer_crewai.tools.create.MainlayerClient.post",
            return_value=SAMPLE_CREATED_RESOURCE,
        ):
            result = tool._run(
                name="My Sentiment API",
                description="Real-time text sentiment analysis",
                type="api",
                fee_model="pay_per_call",
                price=0.005,
                endpoint_url="https://api.example.com/sentiment",
            )

        parsed = json.loads(result)
        assert parsed["id"] == "res_my_api_003"
        assert parsed["status"] == "active"

    def test_run_sends_correct_payload(self) -> None:
        tool = self._make_tool()
        captured_payload: dict = {}

        def mock_post(path: str, payload: dict) -> Any:
            captured_payload.update(payload)
            return SAMPLE_CREATED_RESOURCE

        with patch(
            "mainlayer_crewai.tools.create.MainlayerClient.post",
            side_effect=mock_post,
        ):
            tool._run(
                name="My Sentiment API",
                description="Text sentiment analysis",
                type="api",
                fee_model="pay_per_call",
                price=0.005,
                endpoint_url="https://api.example.com/sentiment",
            )

        assert captured_payload["name"] == "My Sentiment API"
        assert captured_payload["type"] == "api"
        assert captured_payload["fee_model"] == "pay_per_call"
        assert captured_payload["price"] == 0.005
        assert captured_payload["endpoint_url"] == "https://api.example.com/sentiment"

    def test_run_omits_optional_fields_when_none(self) -> None:
        tool = self._make_tool()
        captured_payload: dict = {}

        def mock_post(path: str, payload: dict) -> Any:
            captured_payload.update(payload)
            return SAMPLE_CREATED_RESOURCE

        with patch(
            "mainlayer_crewai.tools.create.MainlayerClient.post",
            side_effect=mock_post,
        ):
            tool._run(
                name="My Sentiment API",
                description="Text sentiment analysis",
                type="api",
                fee_model="pay_per_call",
                price=0.005,
            )

        assert "endpoint_url" not in captured_payload
        assert "metadata" not in captured_payload

    def test_run_includes_metadata_when_provided(self) -> None:
        tool = self._make_tool()
        captured_payload: dict = {}

        def mock_post(path: str, payload: dict) -> Any:
            captured_payload.update(payload)
            return SAMPLE_CREATED_RESOURCE

        meta = {"rate_limit": "100/min", "docs": "https://docs.example.com"}
        with patch(
            "mainlayer_crewai.tools.create.MainlayerClient.post",
            side_effect=mock_post,
        ):
            tool._run(
                name="My Sentiment API",
                description="Text sentiment analysis",
                type="api",
                fee_model="pay_per_call",
                price=0.005,
                metadata=meta,
            )

        assert captured_payload["metadata"] == meta


# ---------------------------------------------------------------------------
# MainlayerToolkit
# ---------------------------------------------------------------------------


class TestMainlayerToolkit:
    def test_get_tools_returns_all_five(self) -> None:
        toolkit = MainlayerToolkit(api_key=API_KEY, wallet_address=WALLET)
        tools = toolkit.get_tools()
        assert len(tools) == 5

    def test_get_buyer_tools_returns_four(self) -> None:
        toolkit = MainlayerToolkit(api_key=API_KEY, wallet_address=WALLET)
        tools = toolkit.get_buyer_tools()
        assert len(tools) == 4

    def test_get_buyer_tools_names(self) -> None:
        toolkit = MainlayerToolkit(api_key=API_KEY, wallet_address=WALLET)
        names = {t.name for t in toolkit.get_buyer_tools()}
        assert "discover_mainlayer_resources" in names
        assert "get_mainlayer_resource_info" in names
        assert "check_mainlayer_access" in names
        assert "pay_for_mainlayer_resource" in names

    def test_get_vendor_tools_returns_one(self) -> None:
        toolkit = MainlayerToolkit(api_key=API_KEY, wallet_address=WALLET)
        tools = toolkit.get_vendor_tools()
        assert len(tools) == 1

    def test_get_vendor_tools_names(self) -> None:
        toolkit = MainlayerToolkit(api_key=API_KEY, wallet_address=WALLET)
        names = {t.name for t in toolkit.get_vendor_tools()}
        assert "create_mainlayer_resource" in names

    def test_all_tools_have_api_key(self) -> None:
        toolkit = MainlayerToolkit(api_key=API_KEY, wallet_address=WALLET)
        for tool in toolkit.get_tools():
            assert tool.api_key == API_KEY  # type: ignore[attr-defined]

    def test_custom_base_url_propagates_to_tools(self) -> None:
        custom_url = "http://localhost:9000"
        toolkit = MainlayerToolkit(api_key=API_KEY, base_url=custom_url)
        for tool in toolkit.get_tools():
            assert tool.base_url == custom_url  # type: ignore[attr-defined]

    def test_get_tools_is_buyer_plus_vendor(self) -> None:
        toolkit = MainlayerToolkit(api_key=API_KEY, wallet_address=WALLET)
        all_names = {t.name for t in toolkit.get_tools()}
        buyer_names = {t.name for t in toolkit.get_buyer_tools()}
        vendor_names = {t.name for t in toolkit.get_vendor_tools()}
        assert all_names == buyer_names | vendor_names


# ---------------------------------------------------------------------------
# MainlayerClient (unit)
# ---------------------------------------------------------------------------


class TestMainlayerClient:
    def test_client_sets_auth_header(self) -> None:
        from mainlayer_crewai._client import MainlayerClient

        mock_resp = MagicMock()
        mock_resp.json.return_value = {"ok": True}
        mock_resp.raise_for_status = MagicMock()

        with patch("httpx.Client") as mock_cls:
            mock_http = MagicMock()
            mock_cls.return_value.__enter__.return_value = mock_http
            mock_http.get.return_value = mock_resp

            client = MainlayerClient(api_key="ml_test", base_url="https://api.mainlayer.xyz")
            client.get("/discover")

        call_kwargs = mock_http.get.call_args
        headers = call_kwargs.kwargs.get("headers") or call_kwargs[1].get("headers", {})
        assert headers["Authorization"] == "Bearer ml_test"

    def test_client_returns_error_dict_on_http_error(self) -> None:
        import httpx

        from mainlayer_crewai._client import MainlayerClient

        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_resp.text = "Forbidden"
        mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "403", request=MagicMock(), response=mock_resp
        )

        with patch("httpx.Client") as mock_cls:
            mock_http = MagicMock()
            mock_cls.return_value.__enter__.return_value = mock_http
            mock_http.get.return_value = mock_resp

            client = MainlayerClient(api_key="ml_test", base_url="https://api.mainlayer.xyz")
            result = client.get("/discover")

        assert "error" in result
        assert "403" in result["error"]

    def test_client_returns_error_dict_on_request_error(self) -> None:
        import httpx

        from mainlayer_crewai._client import MainlayerClient

        with patch("httpx.Client") as mock_cls:
            mock_http = MagicMock()
            mock_cls.return_value.__enter__.return_value = mock_http
            mock_http.get.side_effect = httpx.RequestError("Connection refused")

            client = MainlayerClient(api_key="ml_test", base_url="https://api.mainlayer.xyz")
            result = client.get("/discover")

        assert "error" in result
