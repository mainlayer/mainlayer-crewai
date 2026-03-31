"""Earning crew example — a CrewAI crew that publishes its outputs for sale on Mainlayer.

This example shows how to:
1. Create a crew that generates valuable content (research, analysis, summaries)
2. Publish that output as a paid resource on Mainlayer
3. Monitor earnings from sold resources

Usage:
    MAINLAYER_API_KEY=ml_... OPENAI_API_KEY=sk-... python earning_crew.py
"""

from __future__ import annotations

import os

from crewai import Agent, Crew, Task

from mainlayer_crewai import MonetizedCrew


def main() -> None:
    api_key = os.environ.get("MAINLAYER_API_KEY", "ml_your_key_here")
    openai_key = os.environ.get("OPENAI_API_KEY", "")

    if not openai_key:
        print("Set OPENAI_API_KEY to run this example.")
        return

    # Create a research agent that generates high-quality output
    researcher = Agent(
        role="Research Analyst",
        goal="Generate comprehensive research reports on emerging technologies",
        backstory=(
            "You are an expert research analyst with deep knowledge of AI, blockchain, "
            "and emerging technologies. You create detailed, well-structured reports "
            "that other professionals find valuable and are willing to pay for."
        ),
        llm="gpt-4o",
        verbose=True,
    )

    # Create a task that generates valuable content
    research_task = Task(
        description=(
            "Write a comprehensive research report on the current state of AI agents. "
            "Include: market overview, key players, pricing trends, and future outlook. "
            "Make it detailed enough that AI teams would pay to read it."
        ),
        expected_output=(
            "A 2000-word research report with sections on market size, "
            "key companies, pricing, and 5-year outlook."
        ),
        agent=researcher,
    )

    # Create a MonetizedCrew instead of regular Crew
    crew = MonetizedCrew(
        agents=[researcher],
        tasks=[research_task],
        api_key=api_key,
        verbose=True,
    )

    print("\n--- Starting Research Crew ---")
    print("This crew will generate a research report, then publish it for sale.\n")

    # Execute the crew
    result = crew.kickoff()

    print("\n--- Research Complete ---")
    print("Output preview:")
    print(result[:500] + "..." if len(result) > 500 else result)

    # Publish the output for sale on Mainlayer
    print("\n--- Publishing to Mainlayer ---")
    try:
        resource_id = crew.publish_output(
            name="AI Agent Market Report 2025",
            price_usd=4.99,
            fee_model="one_time",
            description="Comprehensive research on the AI agent market, including trends, key players, and forecasts.",
            output=result,
        )
        print(f"Published successfully! Resource ID: {resource_id}")

        # Create additional resources for different formats of the same research
        summary_id = crew.publish_output(
            name="AI Agent Market Report - Executive Summary",
            price_usd=0.99,
            fee_model="one_time",
            description="1-page executive summary of the AI agent market research.",
            output=result[:800],  # First 800 chars as summary
        )
        print(f"Published summary! Resource ID: {summary_id}")

        # Check earnings
        print("\n--- Checking Earnings ---")
        try:
            earnings = crew.check_earnings()
            print(f"Total earnings: ${earnings.get('total_earned_usd', 0):.2f}")
            print(f"Total transactions: {earnings.get('transaction_count', 0)}")
            if earnings.get("top_resources"):
                print(f"Top resources: {earnings['top_resources']}")
        except RuntimeError as e:
            print(f"Note: {e} (this is normal if no one has purchased yet)")

    except Exception as e:
        print(f"Error publishing: {e}")
        print("Note: Ensure your API key is valid and has the right permissions.")


if __name__ == "__main__":
    main()
