"""Vendor crew example — a CrewAI crew that creates and monetizes a service on Mainlayer.

This example shows a two-agent crew:
- A service architect agent that designs the resource listing
- A publisher agent that creates the resource on Mainlayer

Usage:
    MAINLAYER_API_KEY=ml_... OPENAI_API_KEY=sk-... python vendor_crew.py
"""

from __future__ import annotations

import os

from crewai import Agent, Crew, Task

from mainlayer_crewai import MainlayerToolkit


def main() -> None:
    api_key = os.environ.get("MAINLAYER_API_KEY", "ml_your_key_here")
    openai_key = os.environ.get("OPENAI_API_KEY", "")

    if not openai_key:
        print("Set OPENAI_API_KEY to run this example.")
        return

    toolkit = MainlayerToolkit(api_key=api_key)

    # Agent 1: Designs the resource listing copy and pricing strategy
    strategist = Agent(
        role="Monetization Strategist",
        goal="Design compelling resource listings that attract AI agent buyers on Mainlayer.",
        backstory=(
            "You are an expert at positioning APIs and data services for AI agent consumers. "
            "You write clear, actionable descriptions that help agents understand exactly "
            "what a resource does and why they should pay for it."
        ),
        tools=[],  # No tools needed — this agent just thinks and writes
        llm="gpt-4o",
        verbose=True,
    )

    # Agent 2: Publishes the resource to Mainlayer
    publisher = Agent(
        role="Mainlayer Publisher",
        goal="List new services on Mainlayer and confirm they are active and discoverable.",
        backstory=(
            "You are a technical agent that publishes APIs and data services to the Mainlayer "
            "marketplace. You take resource specifications and create the listings accurately, "
            "then confirm the resource is live with its assigned ID."
        ),
        tools=toolkit.get_vendor_tools(),
        llm="gpt-4o",
        verbose=True,
    )

    # Task 1: Design the listing
    design_task = Task(
        description=(
            "Design a Mainlayer resource listing for a real-time sentiment analysis API. "
            "The API endpoint is https://api.example.com/sentiment. "
            "Decide on: name, description (written for AI agents), type, fee_model, and price in USD. "
            "Output a structured specification that the publisher can use directly."
        ),
        expected_output=(
            "A structured resource specification with: name, description, type, fee_model, "
            "price, and endpoint_url."
        ),
        agent=strategist,
    )

    # Task 2: Publish to Mainlayer
    publish_task = Task(
        description=(
            "Take the resource specification from the strategist and create it on Mainlayer "
            "using the create_mainlayer_resource tool. "
            "Report back the resource_id assigned by Mainlayer and confirm it is active."
        ),
        expected_output=(
            "Confirmation that the resource was created successfully, including the "
            "assigned resource_id and active status."
        ),
        agent=publisher,
        context=[design_task],
    )

    crew = Crew(
        agents=[strategist, publisher],
        tasks=[design_task, publish_task],
        verbose=True,
    )

    result = crew.kickoff()
    print("\n--- Crew Result ---")
    print(result)


if __name__ == "__main__":
    main()
