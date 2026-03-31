"""Research crew example — a crew that discovers and pays for premium data to power research.

This example shows a research team that:
1. Discovers premium data APIs on Mainlayer
2. Evaluates and negotiates pricing
3. Autonomously purchases access to the best data
4. Uses the data to produce research

Usage:
    MAINLAYER_API_KEY=ml_... MAINLAYER_WALLET=0x... OPENAI_API_KEY=sk-... python research_crew.py
"""

from __future__ import annotations

import os

from crewai import Agent, Task, Crew

from mainlayer_crewai import MainlayerToolkit


def main() -> None:
    api_key = os.environ.get("MAINLAYER_API_KEY", "ml_your_key_here")
    wallet = os.environ.get("MAINLAYER_WALLET", "0xYourWalletAddress")
    openai_key = os.environ.get("OPENAI_API_KEY", "")

    if not openai_key:
        print("Set OPENAI_API_KEY to run this example.")
        return

    toolkit = MainlayerToolkit(api_key=api_key, wallet_address=wallet)

    # Scout discovers the best data sources
    scout = Agent(
        role="Data Scout",
        goal="Find the highest-quality market data APIs on Mainlayer",
        backstory=(
            "You are an expert at finding premium data sources. "
            "You specialize in identifying datasets that will give our research team a competitive edge. "
            "You consider data quality, timeliness, and cost-effectiveness."
        ),
        tools=[toolkit.get_buyer_tools()[0]],  # Just discover tool
        llm="gpt-4o",
        verbose=True,
    )

    # Analyst evaluates and purchases
    analyst = Agent(
        role="Budget Analyst",
        goal="Evaluate data APIs and negotiate access at the best price",
        backstory=(
            "You have a keen eye for cost-effective solutions. "
            "You check if we already have access to resources before paying, "
            "and you always look for the best value for our research budget."
        ),
        tools=toolkit.get_buyer_tools()[1:],  # get_info, check_access, pay
        llm="gpt-4o",
        verbose=True,
    )

    # Scout discovers available data
    discover_task = Task(
        description=(
            "Search Mainlayer for financial market data APIs. "
            "Look for real-time stock prices, financial news, or market analysis tools. "
            "Return the top 3 results with their resource_ids, names, and prices."
        ),
        expected_output=(
            "A ranked list of 3 financial data APIs with their resource_ids, "
            "names, prices, and fee models"
        ),
        agent=scout,
    )

    # Analyst evaluates and buys
    purchase_task = Task(
        description=(
            f"From the data sources provided by scout: "
            f"1. Get detailed info on each resource "
            f"2. Check if wallet {wallet} already has access (don't pay twice) "
            f"3. Purchase access to the cheapest option "
            f"Return a summary including: which API you chose, why, and the payment confirmation."
        ),
        expected_output=(
            "A decision summary: selected API, price, existing access status, "
            "and payment confirmation if applicable"
        ),
        agent=analyst,
        context=[discover_task],
    )

    # Run the crew
    crew = Crew(
        agents=[scout, analyst],
        tasks=[discover_task, purchase_task],
        verbose=True,
    )

    print("\n--- Starting Research Data Acquisition ---")
    print("Scout will find data, analyst will evaluate and purchase.\n")

    result = crew.kickoff()

    print("\n--- Data Acquisition Complete ---")
    print(result)
    print(
        "\nYour research team can now use the purchased API to access premium market data!"
    )


if __name__ == "__main__":
    main()
