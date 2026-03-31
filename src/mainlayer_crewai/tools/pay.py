"""PayForResourceTool — pay to access a Mainlayer resource."""

from __future__ import annotations

from typing import Any, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from mainlayer_crewai._client import MainlayerClient


class PayForResourceInput(BaseModel):
    resource_id: str = Field(
        ...,
        description="The ID of the resource to pay for (from discover_mainlayer_resources results).",
    )
    payer_wallet: str = Field(
        ...,
        description="Your wallet address that will be charged for this resource.",
    )


class PayForResourceTool(BaseTool):
    """Pay with Mainlayer to unlock access to a resource."""

    name: str = "pay_for_mainlayer_resource"
    description: str = (
        "Pay with Mainlayer to unlock access to a paid resource or API. "
        "Use this after discover_mainlayer_resources to purchase access to a service your agent needs. "
        "Always run check_mainlayer_access first to avoid duplicate payments. "
        "Returns a payment confirmation with a transaction ID and any access credentials."
    )
    args_schema: Type[BaseModel] = PayForResourceInput

    api_key: str = Field(..., description="Mainlayer API key")
    base_url: str = Field(
        default="https://api.mainlayer.fr",
        description="Mainlayer API base URL",
    )

    def _run(
        self,
        resource_id: str,
        payer_wallet: str,
        **kwargs: Any,
    ) -> str:
        client = MainlayerClient(api_key=self.api_key, base_url=self.base_url)
        payload = {"resource_id": resource_id, "payer_wallet": payer_wallet}
        data = client.post("/pay", payload)
        return client.format(data)
