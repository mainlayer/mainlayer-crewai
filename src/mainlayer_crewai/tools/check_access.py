"""CheckAccessTool — verify whether a wallet has active access to a resource."""

from __future__ import annotations

from typing import Any, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from mainlayer_crewai._client import MainlayerClient


class CheckAccessInput(BaseModel):
    resource_id: str = Field(
        ...,
        description="The ID of the resource to check access for (from discover_mainlayer_resources results).",
    )
    payer_wallet: str = Field(
        ...,
        description="The wallet address to check access for.",
    )


class CheckAccessTool(BaseTool):
    """Check whether a wallet has active paid access to a Mainlayer resource."""

    name: str = "check_mainlayer_access"
    description: str = (
        "Check whether your wallet has active paid access to a Mainlayer resource. "
        "Always run this before pay_for_mainlayer_resource to avoid double-paying. "
        "Returns access status (true/false), expiry time, and remaining credits if the resource is pay-per-call. "
        "If has_access is false, use pay_for_mainlayer_resource to purchase access."
    )
    args_schema: Type[BaseModel] = CheckAccessInput

    api_key: str = Field(..., description="Mainlayer API key")
    base_url: str = Field(
        default="https://api.mainlayer.xyz",
        description="Mainlayer API base URL",
    )

    def _run(
        self,
        resource_id: str,
        payer_wallet: str,
        **kwargs: Any,
    ) -> str:
        client = MainlayerClient(api_key=self.api_key, base_url=self.base_url)
        params = {"resource_id": resource_id, "payer_wallet": payer_wallet}
        data = client.get("/entitlements/check", params=params)
        return client.format(data)
