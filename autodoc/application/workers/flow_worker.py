"""
Flow worker module for AutoDoc.
Analyzes business logic and algorithms, generating Mermaid flowchart diagrams.
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

FLOW_WORKER_SYSTEM_PROMPT = """
You are the Flow Worker for AutoDoc. Your job is to:
1. Identify key business logic flows or algorithms in the project.
2. Generate Mermaid DSL for a flowchart diagram.
3. Use the tools provided to explore the code.
4. IMPORTANT: ALL node labels MUST be wrapped in double quotes. 
   - ALWAYS use `A["Label Text"]` or `A(["Label Text"])` or `A{"Label Text"}`.
   - NEVER use `A[Label Text]` or `A(Label Text)` without quotes.
   - If the label itself contains quotes, use single quotes inside the double-quoted label (e.g., A["Return 'success'"]).
   - DO NOT include brackets `[` or `]` inside the label text as they can break the Mermaid parser even when quoted. Replace them with parentheses `()` if necessary.

Example Mermaid Flowchart:
```mermaid
graph TD
    A["Start Process"] --> B{"Is input valid?"}
    B -- "Yes" --> C["Execute logic (Step 1)"]
    B -- "No" --> D["Return error response"]
    C --> E["End Process"]
    D --> E
```

Focus on the internal logic of complex functions or processes.
Output ONLY the Mermaid DSL code block.
"""


def flow_worker_node(state: AgentState, config=None):
    """
    The Flow worker node that extracts application flows and generates Mermaid DSL.

    Args:
        state: The current agent state.
        config: Runnable configuration.

    Returns:
        Updated state with documentation.
    """
    print("--- Flow Worker Started ---")
    on_event = config.get("configurable", {}).get("on_event") if config else None
    messages = [
        SystemMessage(content=FLOW_WORKER_SYSTEM_PROMPT),
    ] + list(state["messages"])

    agent = create_worker_graph(
        llm, [list_directory, read_file, grep_search], FLOW_WORKER_SYSTEM_PROMPT
    )

    final_response, events = run_worker_graph(agent, messages, "FlowWorker", on_event)

    code, explanation = extract_diagram_result(llm, final_response["messages"])
    dsl = clean_mermaid_dsl(code)

    new_documentation = []

    if dsl:
        result = validate_mermaid(dsl)
        if result["success"]:
            new_documentation.append(
                {
                    "type": "flows",
                    "explanation": explanation,
                    "code": dsl,
                    "valid": True,
                }
            )
        else:
            warning_msg = (
                f"\n\n> [!WARNING]\n> Failed to validate Flow "
                f"Mermaid DSL: {result['error']}"
            )
            new_documentation.append(
                {
                    "type": "flows",
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
