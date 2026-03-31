"""MonetizedCrew — a CrewAI crew that publishes its outputs for sale on Mainlayer."""

from __future__ import annotations

from typing import Optional, List, Dict, Any

from crewai import Agent, Crew, Task

from mainlayer_crewai._client import MainlayerClient
from mainlayer_crewai.toolkit import MainlayerToolkit


class MonetizedCrew(Crew):
    """A CrewAI crew that can publish its generated outputs as paid resources.

    This class extends Crew to enable automatic monetization of crew output.
    After the crew completes a task, the result can be published to Mainlayer
    as a paid resource that other agents can discover and purchase.

    Example usage:

        toolkit = MainlayerToolkit(api_key="ml_...", wallet_address="0x...")

        summarizer = Agent(
            role="Summarization Agent",
            goal="Create accurate, concise summaries",
            tools=[],
            llm="gpt-4o",
        )

        task = Task(
            description="Summarize this research paper...",
            expected_output="A 500-word summary",
            agent=summarizer,
        )

        crew = MonetizedCrew(
            agents=[summarizer],
            tasks=[task],
            api_key="ml_...",
        )

        result = crew.kickoff()

        # Publish the output as a paid resource
        resource_id = crew.publish_output(
            name="Research Paper Summary",
            output=result,
            price_usd=0.25,
            fee_model="one_time",
            description="AI-generated summary of academic research",
        )
        print(f"Published to Mainlayer: {resource_id}")
    """

    def __init__(
        self,
        agents: List[Agent],
        tasks: List[Task],
        api_key: str,
        verbose: bool = False,
        memory: bool = True,
        cache: bool = True,
        max_iter: int = 15,
        number_of_groups: Optional[int] = None,
    ) -> None:
        """Initialize a monetized crew.

        Args:
            agents: List of CrewAI agents in the crew
            tasks: List of CrewAI tasks to execute
            api_key: Mainlayer API key for publishing resources
            verbose: Whether to log crew execution
            memory: Whether to enable crew memory
            cache: Whether to enable crew cache
            max_iter: Maximum iterations per task
            number_of_groups: Number of agent groups for group chats
        """
        super().__init__(
            agents=agents,
            tasks=tasks,
            verbose=verbose,
            memory=memory,
            cache=cache,
            max_iter=max_iter,
        )
        self.api_key = api_key
        self.client = MainlayerClient(api_key=api_key)
        self._last_output: Optional[str] = None

    def kickoff(self, inputs: Optional[Dict[str, Any]] = None) -> str:
        """Execute the crew and store the output.

        Args:
            inputs: Input variables for the crew

        Returns:
            The crew's output
        """
        result = super().kickoff(inputs=inputs)  # type: ignore
        self._last_output = str(result)
        return self._last_output

    def publish_output(
        self,
        name: str,
        price_usd: float,
        fee_model: str = "one_time",
        description: Optional[str] = None,
        output: Optional[str] = None,
    ) -> str:
        """Publish the crew's output as a paid resource on Mainlayer.

        Args:
            name: Display name for the resource
            price_usd: Price in USD (must be >= 0)
            fee_model: Pricing model - "one_time", "subscription", or "pay_per_call"
            description: Optional description of the resource
            output: Output to publish. If None, uses the last crew.kickoff() result

        Returns:
            The created resource_id on Mainlayer

        Raises:
            ValueError: If no output is available to publish
        """
        if output is None:
            output = self._last_output

        if not output:
            raise ValueError(
                "No output to publish. Either run crew.kickoff() first or pass output parameter."
            )

        payload: Dict[str, Any] = {
            "name": name,
            "price_usd": price_usd,
            "fee_model": fee_model,
        }

        if description:
            payload["description"] = description

        data = self.client.post("/resources", payload)

        if "error" in data:
            raise RuntimeError(f"Failed to publish resource: {data['error']}")

        resource_id = data.get("id") or data.get("resource_id")
        if not resource_id:
            raise RuntimeError(f"No resource_id in response: {data}")

        return resource_id

    def check_earnings(self) -> Dict[str, Any]:
        """Retrieve the crew's total earnings from published resources.

        Returns:
            Analytics dict with total earnings and transaction details
        """
        data = self.client.get("/analytics/revenue")

        if "error" in data:
            raise RuntimeError(f"Failed to fetch earnings: {data['error']}")

        return data
