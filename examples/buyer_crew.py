"""Buyer crew example — a CrewAI agent that autonomously discovers and pays for services.

This example shows a research agent that:
1. Searches Mainlayer for a weather data API
2. Checks if it already has access
3. Pays for access if needed
4. Reports back with the resource details

Usage:
    MAINLAYER_API_KEY=ml_... MAINLAYER_WALLET=0x... OPENAI_API_KEY=sk-... python buyer_crew.py
"""

from __future__ import annotations

import os

from crewai import Agent, Crew, Task

from mainlayer_crewai import MainlayerToolkit


def main() -> None:
    api_key = os.environ.get("MAINLAYER_API_KEY", "ml_your_key_here")
    wallet = os.environ.get("MAINLAYER_WALLET", "0xYourWalletAddress")
    openai_key = os.environ.get("OPENAI_API_KEY", "")

    if not openai_key:
        print("Set OPENAI_API_KEY to run this example.")
        return

    toolkit = MainlayerToolkit(api_key=api_key, wallet_address=wallet)

    researcher = Agent(
        role="API Research Agent",
        goal="Find the best paid data services on Mainlayer and acquire access for the team.",
        backstory=(
            "You are a resourceful AI agent that specialises in discovering and procuring "
            "data APIs and services. You always check for existing access before paying, "
            "and you provide clear summaries of what you found and what actions you took."
        ),
        tools=toolkit.get_buyer_tools(),
        llm="gpt-4o",
        verbose=True,
    )

    task = Task(
        description=(
            f"Search Mainlayer for a weather data API. "
            f"Check if wallet {wallet} already has access to it. "
            f"If not, pay for access using Mainlayer payments. "
            f"Return a summary including: the resource name, its resource_id, "
            f"the price, and whether payment was required."
        ),
        expected_output=(
            "A concise summary with: resource name, resource_id, price, fee model, "
            "whether we already had access, and the payment transaction ID if a payment was made."
        ),
        agent=researcher,
    )

    crew = Crew(
        agents=[researcher],
        tasks=[task],
        verbose=True,
    )

    result = crew.kickoff()
    print("\n--- Crew Result ---")
    print(result)


if __name__ == "__main__":
    main()
