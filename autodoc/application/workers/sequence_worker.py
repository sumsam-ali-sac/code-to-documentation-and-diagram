"""
Sequence worker for the AutoDoc system.
Identifies business logic flows and generates Mermaid sequence diagrams.
"""

import os

from langchain_core.messages import SystemMessage
from langchain_openai import AzureChatOpenAI

from autodoc.application.workers.base_worker import (
    create_worker_graph,
    extract_diagram_result,
    run_worker_graph,
)
from autodoc.domain.state import AgentState
from autodoc.infrastructure.engine.validator import clean_mermaid_dsl, validate_mermaid
from autodoc.infrastructure.tools.code_scanner import (
    grep_search,
    list_directory,
    read_file,
)

llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview"),
)

SEQUENCE_WORKER_SYSTEM_PROMPT = """
You are the Sequence Worker for AutoDoc. Your job is to:
1. Identify key business logic flows3. Use the tools provided to find the relevant code.
4. IMPORTANT: When defining aliases or labels in Mermaid that contain spaces or special characters, you MUST wrap the text in double quotes. DO NOT use double quotes INSIDE the label itself; if you need to include quotes or strings (like JSON), use single quotes (e.g., A["Return {'key':'value'}"]).
5. Generate the Mermaid DSL for the sequence diagram.

Example Mermaid Sequence Diagram:
```mermaid
sequenceDiagram
    participant Client
    participant API
    participant DB
    Client->>API: GET /users
    API->>DB: Query Users
    DB-->>API: User Data
    API-->>Client: 200 OK
```

Focus on the interaction between components.
Output ONLY the Mermaid DSL code block.
"""


def sequence_worker_node(state: AgentState, config=None):
    """
    The Sequence worker node that extracts request/response cycles and generates Mermaid DSL.

    Args:
        state: The current agent state.
        config: Runnable configuration.

    Returns:
        Updated state with documentation.
    """
    print("--- Sequence Worker Started ---")
    on_event = config.get("configurable", {}).get("on_event") if config else None
    messages = [
        SystemMessage(content=SEQUENCE_WORKER_SYSTEM_PROMPT),
    ] + list(state["messages"])

    agent = create_worker_graph(
        llm, [list_directory, read_file, grep_search], SEQUENCE_WORKER_SYSTEM_PROMPT
    )

    final_response, events = run_worker_graph(
        agent, messages, "SequenceWorker", on_event
    )

    code, explanation = extract_diagram_result(llm, final_response["messages"])
    dsl = clean_mermaid_dsl(code)

    new_documentation = []

    if dsl:
        result = validate_mermaid(dsl)
        if result["success"]:
            new_documentation.append(
                {
                    "type": "sequence",
                    "explanation": explanation,
                    "code": dsl,
                    "valid": True,
                }
            )
        else:
            warning_msg = (
                f"\n\n> [!WARNING]\n> Failed to validate Sequence "
                f"Mermaid DSL: {result['error']}"
            )
            new_documentation.append(
                {
                    "type": "sequence",
                    "explanation": explanation + warning_msg,
                    "code": "",
                    "valid": False,
                }
            )

    return {
        "messages": final_response["messages"],
        "documentation": new_documentation,
        "events": events,
    }
