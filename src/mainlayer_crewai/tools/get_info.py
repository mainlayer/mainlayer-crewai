"""GetResourceInfoTool — fetch full details for a specific Mainlayer resource."""

from __future__ import annotations

from typing import Any, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from mainlayer_crewai._client import MainlayerClient


class GetResourceInfoInput(BaseModel):
    resource_id: str = Field(
        ...,
        description="The ID of the resource to retrieve full details for.",
    )


class GetResourceInfoTool(BaseTool):
    """Retrieve complete details for a specific Mainlayer resource by its ID."""

    name: str = "get_mainlayer_resource_info"
    description: str = (
        "Retrieve complete details for a specific Mainlayer resource by its ID. "
        "Use this after discover_mainlayer_resources when you need full information about a resource — "
        "including its endpoint URL, detailed description, pricing breakdown, and availability status. "
        "Requires a resource_id obtained from discover_mainlayer_resources results."
    )
    args_schema: Type[BaseModel] = GetResourceInfoInput

    api_key: str = Field(..., description="Mainlayer API key")
    base_url: str = Field(
        default="https://api.mainlayer.xyz",
        description="Mainlayer API base URL",
    )

    def _run(
        self,
        resource_id: str,
        **kwargs: Any,
    ) -> str:
        client = MainlayerClient(api_key=self.api_key, base_url=self.base_url)
        data = client.get(f"/resources/public/{resource_id}")
        return client.format(data)
