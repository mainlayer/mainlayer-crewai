"""MainlayerToolkit — bundles all Mainlayer CrewAI tools into a single object."""

from __future__ import annotations

from typing import List, Optional

from crewai.tools import BaseTool

from mainlayer_crewai.tools.check_access import CheckAccessTool
from mainlayer_crewai.tools.create import CreateResourceTool
from mainlayer_crewai.tools.discover import DiscoverResourcesTool
from mainlayer_crewai.tools.get_info import GetResourceInfoTool
from mainlayer_crewai.tools.pay import PayForResourceTool


class MainlayerToolkit:
    """Toolkit that provides all Mainlayer payment tools for CrewAI agents.

    Example usage::

        from mainlayer_crewai import MainlayerToolkit
        from crewai import Agent, Task, Crew

        toolkit = MainlayerToolkit(api_key="ml_...", wallet_address="0x...")

        researcher = Agent(
            role="Research Agent",
            goal="Find and use the best paid AI data services",
            backstory="An agent that autonomously discovers and pays for APIs it needs.",
            tools=toolkit.get_buyer_tools(),
            llm="gpt-4o",
        )

        task = Task(
            description=(
                "Find a weather data API on Mainlayer, check if you already have access, "
                "and pay for it if needed. Return the resource details."
            ),
            expected_output="A summary of the resource found and payment status.",
            agent=researcher,
        )

        crew = Crew(agents=[researcher], tasks=[task])
        result = crew.kickoff()
        print(result)
    """

    def __init__(
        self,
        api_key: str,
        wallet_address: Optional[str] = None,
        base_url: str = "https://api.mainlayer.fr",
    ) -> None:
        """Initialise the toolkit.

        Args:
            api_key: Your Mainlayer API key (starts with ``ml_``).
            wallet_address: Default wallet address used as ``payer_wallet`` in buyer
                tools. Passed into tools that accept a wallet but can be overridden
                at the task level by the agent.
            base_url: Override the Mainlayer API base URL. Useful for testing against
                a local server or staging environment.
        """
        self.api_key = api_key
        self.wallet_address = wallet_address
        self.base_url = base_url

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _shared_kwargs(self) -> dict:
        return {"api_key": self.api_key, "base_url": self.base_url}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_tools(self) -> List[BaseTool]:
        """Return all Mainlayer tools — buyer tools plus vendor tools.

        Returns:
            A list of :class:`BaseTool` instances ready to assign to any
            CrewAI :class:`~crewai.Agent` via its ``tools`` parameter.
        """
        return [*self.get_buyer_tools(), *self.get_vendor_tools()]

    def get_buyer_tools(self) -> List[BaseTool]:
        """Return buyer-facing tools: discover, get info, check access, and pay.

        These tools are suitable for agents that consume paid services on Mainlayer.
        """
        kwargs = self._shared_kwargs()
        return [
            DiscoverResourcesTool(**kwargs),
            GetResourceInfoTool(**kwargs),
            CheckAccessTool(**kwargs),
            PayForResourceTool(**kwargs),
        ]

    def get_vendor_tools(self) -> List[BaseTool]:
        """Return vendor-facing tools: create resource.

        These tools are suitable for agents that produce and monetize services
        on the Mainlayer marketplace.
        """
        kwargs = self._shared_kwargs()
        return [
            CreateResourceTool(**kwargs),
        ]
