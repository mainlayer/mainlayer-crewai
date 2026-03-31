"""DiscoverResourcesTool — search for paid resources on the Mainlayer marketplace."""

from __future__ import annotations

from typing import Any, Dict, Optional, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from mainlayer_crewai._client import MainlayerClient


class DiscoverResourcesInput(BaseModel):
    query: str = Field(
        default="",
        description="Keyword search query — e.g. 'weather data', 'financial news', 'translation API'",
    )
    type: str = Field(
        default="",
        description="Filter by resource type. One of: api, file, endpoint, page. Leave blank for all types.",
    )
    fee_model: str = Field(
        default="",
        description=(
            "Filter by pricing model. One of: one_time, subscription, pay_per_call. "
            "Leave blank for all pricing models."
        ),
    )
    limit: int = Field(
        default=20,
        description="Maximum number of results to return (default 20, max 100).",
    )


class DiscoverResourcesTool(BaseTool):
    """Search for paid resources, APIs, and services on the Mainlayer marketplace."""

    name: str = "discover_mainlayer_resources"
    description: str = (
        "Search for paid resources, APIs, and services on Mainlayer — the payment marketplace for AI agents. "
        "Use this tool first to find services your agent needs to access. "
        "Returns a list of available resources with their IDs, names, descriptions, pricing models, and prices. "
        "The resource_id from results is required for pay_for_mainlayer_resource and check_mainlayer_access."
    )
    args_schema: Type[BaseModel] = DiscoverResourcesInput

    api_key: str = Field(..., description="Mainlayer API key")
    base_url: str = Field(
        default="https://api.mainlayer.fr",
        description="Mainlayer API base URL",
    )

    def _run(
        self,
        query: str = "",
        type: str = "",
        fee_model: str = "",
        limit: int = 20,
        **kwargs: Any,
    ) -> str:
        client = MainlayerClient(api_key=self.api_key, base_url=self.base_url)
        params: Dict[str, Any] = {"q": query, "limit": limit}
        if type:
            params["type"] = type
        if fee_model:
            params["fee_model"] = fee_model

        data = client.get("/discover", params=params)

        if "error" in data:
            return client.format(data)

        resources = data if isinstance(data, list) else data.get("resources", data)
        return client.format(resources)
