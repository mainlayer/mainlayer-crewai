"""CreateResourceTool — register a new paid resource on Mainlayer (vendor use)."""

from __future__ import annotations

from typing import Any, Dict, Optional, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from mainlayer_crewai._client import MainlayerClient


class CreateResourceInput(BaseModel):
    name: str = Field(
        ...,
        description="Display name for the resource as it will appear in the Mainlayer marketplace.",
    )
    description: str = Field(
        ...,
        description="Clear description of what the resource provides, written for AI agents that will discover it.",
    )
    type: str = Field(
        ...,
        description="Resource type. Must be one of: api, file, endpoint, page.",
    )
    fee_model: str = Field(
        ...,
        description="Pricing model. Must be one of: one_time, subscription, pay_per_call.",
    )
    price: float = Field(
        ...,
        description="Price in USD. For pay_per_call this is the per-call price. For subscription, the monthly price.",
    )
    endpoint_url: Optional[str] = Field(
        default=None,
        description="The URL of the API or endpoint being monetized (optional but recommended for api/endpoint types).",
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional key-value metadata for the resource, such as rate limits or documentation links.",
    )


class CreateResourceTool(BaseTool):
    """Create and list a new paid resource on Mainlayer so other agents can discover and pay to use it."""

    name: str = "create_mainlayer_resource"
    description: str = (
        "Create and list a new paid resource on Mainlayer so other AI agents can discover and pay to use it. "
        "Use this to monetize APIs, datasets, or services your agent provides. "
        "Required fields: name, description, type (api/file/endpoint/page), "
        "fee_model (one_time/subscription/pay_per_call), price (USD). "
        "Returns the newly created resource with its assigned resource_id and active status."
    )
    args_schema: Type[BaseModel] = CreateResourceInput

    api_key: str = Field(..., description="Mainlayer API key")
    base_url: str = Field(
        default="https://api.mainlayer.xyz",
        description="Mainlayer API base URL",
    )

    def _run(
        self,
        name: str,
        description: str,
        type: str,
        fee_model: str,
        price: float,
        endpoint_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> str:
        client = MainlayerClient(api_key=self.api_key, base_url=self.base_url)
        payload: Dict[str, Any] = {
            "name": name,
            "description": description,
            "type": type,
            "fee_model": fee_model,
            "price": price,
        }
        if endpoint_url:
            payload["endpoint_url"] = endpoint_url
        if metadata:
            payload["metadata"] = metadata

        data = client.post("/resources", payload)
        return client.format(data)
