# mainlayer-crewai

CrewAI tools for [Mainlayer](https://mainlayer.xyz) — payment infrastructure for AI agents.

Give your CrewAI agents the ability to discover paid services, check access, and pay for them autonomously — all within a crew.

## Installation

```bash
pip install mainlayer-crewai
```

With OpenAI support for the examples:

```bash
pip install "mainlayer-crewai[openai]"
```

## Quick Start

```python
from crewai import Agent, Task, Crew
from mainlayer_crewai import MainlayerToolkit

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
        "Find a weather data API on Mainlayer. "
        "Check if you already have access, and pay for it if needed. "
        "Return the resource name, ID, and payment status."
    ),
    expected_output="Resource name, ID, price, and payment confirmation if applicable.",
    agent=researcher,
)

crew = Crew(agents=[researcher], tasks=[task])
result = crew.kickoff()
print(result)
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
    base_url="https://api.mainlayer.xyz",  # override for testing
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

Get your API key from [mainlayer.xyz](https://mainlayer.xyz). Keys start with `ml_`.

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

- [Mainlayer](https://mainlayer.xyz)
- [Documentation](https://docs.mainlayer.xyz)
- [Issues](https://github.com/mainlayer/mainlayer-crewai/issues)
