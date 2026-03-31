# mainlayer-crewai

[![PyPI](https://img.shields.io/pypi/v/mainlayer-crewai.svg)](https://pypi.org/project/mainlayer-crewai/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Production-ready CrewAI tools for [Mainlayer](https://mainlayer.fr) — payment infrastructure for AI agents.

Build autonomous AI crews that discover, pay for, and monetize services on the Mainlayer marketplace. Enable your agents to earn revenue, access premium APIs, and coordinate multi-agent commerce workflows.

## Installation

```bash
pip install mainlayer-crewai
```

With OpenAI models for the examples:

```bash
pip install "mainlayer-crewai[openai]"
```

With dev dependencies for testing:

```bash
pip install "mainlayer-crewai[dev]"
```

## 5-Minute Quickstart

```python
from crewai import Agent, Task, Crew
from mainlayer_crewai import MainlayerToolkit
import os

# Initialize the toolkit with your Mainlayer credentials
toolkit = MainlayerToolkit(
    api_key=os.environ["MAINLAYER_API_KEY"],
    wallet_address=os.environ["MAINLAYER_WALLET"]
)

# Create a crew that discovers and pays for a service
researcher = Agent(
    role="Research Agent",
    goal="Find and acquire the best paid data services on Mainlayer",
    backstory="An autonomous agent that discovers, evaluates, and purchases APIs.",
    tools=toolkit.get_buyer_tools(),
    llm="gpt-4o",
)

task = Task(
    description="Search Mainlayer for a weather data API, check access, and pay if needed.",
    expected_output="Resource name, ID, price, and payment status.",
    agent=researcher,
)

crew = Crew(agents=[researcher], tasks=[task])
result = crew.kickoff()
print(result)
```

## Use Cases

### 1. Research Crew — Autonomous Data Acquisition

A crew that discovers premium data APIs, evaluates pricing, checks existing access, and autonomously purchases access when needed.

```python
from crewai import Agent, Task, Crew
from mainlayer_crewai import MainlayerToolkit

toolkit = MainlayerToolkit(api_key="ml_...", wallet_address="0x...")

# Scout discovers the best service
scout = Agent(
    role="Research Scout",
    goal="Find the best financial data APIs",
    backstory="Expert at finding premium data sources",
    tools=[toolkit.get_buyer_tools()[0]],  # discover only
    llm="gpt-4o",
)

# Analyst evaluates and purchases
analyst = Agent(
    role="Budget Analyst",
    goal="Acquire the most cost-effective data service",
    backstory="Negotiates and purchases on behalf of the research team",
    tools=toolkit.get_buyer_tools()[1:],  # get_info, check_access, pay
    llm="gpt-4o",
)

discover_task = Task(
    description="Find the top 3 financial data APIs and return their resource_ids",
    expected_output="list of resource_ids",
    agent=scout,
)

purchase_task = Task(
    description=f"Check if wallet 0x... has access to the APIs from scout. Pay for the cheapest one.",
    expected_output="Payment confirmation and access token",
    agent=analyst,
    context=[discover_task],
)

crew = Crew(agents=[scout, analyst], tasks=[discover_task, purchase_task])
result = crew.kickoff()
```

### 2. Monetized Crew — Agents That Earn Revenue

A crew that creates and sells AI services, monitoring earnings and optimizing pricing.

```python
from crewai import Agent, Task, Crew
from mainlayer_crewai import MainlayerToolkit

toolkit = MainlayerToolkit(api_key="ml_...")

# Vendor creates resources and monitors revenue
vendor = Agent(
    role="API Vendor Manager",
    goal="Publish AI services on Mainlayer and maximize revenue",
    backstory="Manages the marketplace presence of our AI services",
    tools=toolkit.get_vendor_tools() + toolkit.get_buyer_tools(),
    llm="gpt-4o",
)

task = Task(
    description=(
        "Create 3 new resources for our sentiment analysis, translation, and summarization APIs. "
        "Set pricing at $0.01, $0.02, and $0.005 per call respectively. "
        "Then check our total earnings."
    ),
    expected_output="Created resource IDs and current earnings",
    agent=vendor,
)

crew = Crew(agents=[vendor], tasks=[task])
result = crew.kickoff()
```

### 3. Multi-Agent Commerce — Complete Payment Flow

A crew where vendors publish services and buyers discover, evaluate, and purchase them in a coordinated workflow.

```python
from crewai import Agent, Task, Crew
from mainlayer_crewai import MainlayerToolkit

vendor_toolkit = MainlayerToolkit(api_key="ml_vendor_key")
buyer_toolkit = MainlayerToolkit(
    api_key="ml_buyer_key",
    wallet_address="0xbuyer..."
)

# Vendor publishes a service
vendor = Agent(
    role="Service Publisher",
    goal="Publish our services on Mainlayer",
    tools=vendor_toolkit.get_vendor_tools(),
    llm="gpt-4o",
)

# Buyer discovers and purchases
buyer = Agent(
    role="Service Buyer",
    goal="Find and purchase the best available services",
    tools=buyer_toolkit.get_buyer_tools(),
    llm="gpt-4o",
)

publish_task = Task(
    description="Create a resource called 'Advanced Analytics API' at $0.10 per call",
    expected_output="resource_id of created resource",
    agent=vendor,
)

purchase_task = Task(
    description="Search for 'analytics' on Mainlayer, find the Advanced Analytics API, and purchase it",
    expected_output="Payment confirmation",
    agent=buyer,
)

crew = Crew(
    agents=[vendor, buyer],
    tasks=[publish_task, purchase_task],
)
result = crew.kickoff()
```

## Available Tools

| Class | Tool name | Description |
|---|---|---|
| `DiscoverResourcesTool` | `discover_mainlayer_resources` | Search for paid APIs and services on the Mainlayer marketplace |
| `GetResourceInfoTool` | `get_mainlayer_resource_info` | Retrieve full details for a specific resource by ID |
| `CheckAccessTool` | `check_mainlayer_access` | Check whether your wallet has active access to a resource |
| `PayForResourceTool` | `pay_for_mainlayer_resource` | Pay with Mainlayer to unlock access to a resource |
| `CreateResourceTool` | `create_mainlayer_resource` | Create and list a new paid resource (vendor use) |

## Toolkit

The `MainlayerToolkit` bundles all tools and injects your credentials:

```python
from mainlayer_crewai import MainlayerToolkit

toolkit = MainlayerToolkit(
    api_key="ml_...",
    wallet_address="0x...",        # used as payer_wallet in buyer tools
    base_url="https://api.mainlayer.fr",  # override for testing
)

tools = toolkit.get_tools()         # all 5 tools
tools = toolkit.get_buyer_tools()   # discover + get_info + check_access + pay (4 tools)
tools = toolkit.get_vendor_tools()  # create (1 tool)
```

## Agent Patterns

### Buyer agent — discover and pay for a service

```python
from crewai import Agent, Task, Crew
from mainlayer_crewai import MainlayerToolkit

toolkit = MainlayerToolkit(api_key="ml_...", wallet_address="0x...")

buyer = Agent(
    role="Data Acquisition Agent",
    goal="Source the best financial data APIs at the lowest cost",
    backstory=(
        "You are an expert at finding and procuring data services. "
        "You always check for existing access before paying."
    ),
    tools=toolkit.get_buyer_tools(),
    llm="gpt-4o",
)

task = Task(
    description=(
        "Find a financial data API on Mainlayer with a pay_per_call fee model. "
        "Check if wallet 0x... already has access. Pay if needed."
    ),
    expected_output="Resource details and payment status.",
    agent=buyer,
)

Crew(agents=[buyer], tasks=[task]).kickoff()
```

### Vendor agent — monetize a service

```python
from crewai import Agent, Task, Crew
from mainlayer_crewai import MainlayerToolkit

toolkit = MainlayerToolkit(api_key="ml_...")

vendor = Agent(
    role="API Monetization Agent",
    goal="List our APIs on Mainlayer and confirm they are discoverable",
    backstory="You publish APIs to the Mainlayer marketplace so other agents can pay to use them.",
    tools=toolkit.get_vendor_tools(),
    llm="gpt-4o",
)

task = Task(
    description=(
        "Create a new Mainlayer resource for our sentiment analysis API at "
        "https://api.example.com/sentiment. "
        "Set the fee model to pay_per_call at $0.005 per call."
    ),
    expected_output="The created resource ID and confirmation it is active.",
    agent=vendor,
)

Crew(agents=[vendor], tasks=[task]).kickoff()
```

### Multi-agent crew

```python
from crewai import Agent, Task, Crew
from mainlayer_crewai import MainlayerToolkit

toolkit = MainlayerToolkit(api_key="ml_...", wallet_address="0x...")

# Agent 1: finds the best resource
scout = Agent(
    role="Resource Scout",
    goal="Find the best translation API on Mainlayer",
    tools=[toolkit.get_buyer_tools()[0]],  # discover only
    llm="gpt-4o",
)

# Agent 2: acquires access
buyer = Agent(
    role="Procurement Agent",
    goal="Check access and pay for resources the scout identifies",
    tools=toolkit.get_buyer_tools()[1:],  # get_info + check + pay
    llm="gpt-4o",
)

scout_task = Task(
    description="Search Mainlayer for translation APIs and return the top result's resource_id.",
    expected_output="resource_id of the best translation API.",
    agent=scout,
)

buy_task = Task(
    description="Check access and pay for the resource_id from the scout. Wallet: 0x...",
    expected_output="Payment confirmation or confirmation that access already exists.",
    agent=buyer,
    context=[scout_task],
)

Crew(agents=[scout, buyer], tasks=[scout_task, buy_task]).kickoff()
```

## Using Tools Directly

```python
from mainlayer_crewai import DiscoverResourcesTool, CheckAccessTool, PayForResourceTool

# Discover
discover = DiscoverResourcesTool(api_key="ml_...")
resources = discover._run(query="weather", type="api", fee_model="pay_per_call")

# Check access
check = CheckAccessTool(api_key="ml_...")
status = check._run(resource_id="res_abc123", payer_wallet="0x...")

# Pay
pay = PayForResourceTool(api_key="ml_...")
receipt = pay._run(resource_id="res_abc123", payer_wallet="0x...")
```

## Running Tests

```bash
pip install "mainlayer-crewai[dev]"
pytest tests/ -v
```

## Authentication

Get your API key from [mainlayer.fr](https://mainlayer.fr). Keys start with `ml_`.

Set it as an environment variable and read it at runtime:

```python
import os
from mainlayer_crewai import MainlayerToolkit

toolkit = MainlayerToolkit(
    api_key=os.environ["MAINLAYER_API_KEY"],
    wallet_address=os.environ["MAINLAYER_WALLET"],
)
```

## Links

- [Mainlayer](https://mainlayer.fr)
- [Documentation](https://docs.mainlayer.fr)
- [Issues](https://github.com/mainlayer/mainlayer-crewai/issues)
