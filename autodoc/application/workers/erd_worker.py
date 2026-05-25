"""
ERD worker module for AutoDoc.
Analyzes database models and relationships, generating Mermaid Entity Relationship Diagrams.
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

ERD_WORKER_SYSTEM_PROMPT = """
You are the ERD Worker for AutoDoc. Your job is to:
1. Identify database models and their relationships in the project.
3. Use the tools provided to explore the project.
4. IMPORTANT: When defining node labels or string literals in Mermaid that contain spaces or special characters (like parentheses, brackets, or commas), you MUST wrap the text in double quotes. DO NOT use double quotes INSIDE the label itself; if you need to include quotes or strings (like JSON), use single quotes (e.g., A["Return {'key':'value'}"]).
5. Generate the Mermaid DSL for the ERD.

Example Mermaid ERD:
```mermaid
erDiagram
    USER ||--o{ POST : writes
    USER {
        string username
        string email
    }
    POST {
        string title
        string content
    }
```

Output ONLY the Mermaid DSL code block.
"""


def erd_worker_node(state: AgentState, config=None):
    """
    The ERD worker node that extracts database schema and generates Mermaid DSL.

    Args:
        state: The current agent state.
        config: Runnable configuration.

    Returns:
        Updated state with documentation.
    """
    print("--- ERD Worker Started ---")
    on_event = config.get("configurable", {}).get("on_event") if config else None
    messages = [
        SystemMessage(content=ERD_WORKER_SYSTEM_PROMPT),
    ] + list(state["messages"])

    agent = create_worker_graph(
        llm, [list_directory, read_file, grep_search], ERD_WORKER_SYSTEM_PROMPT
    )

    final_response, events = run_worker_graph(agent, messages, "ERDWorker", on_event)

    code, explanation = extract_diagram_result(llm, final_response["messages"])
    dsl = clean_mermaid_dsl(code)

    new_documentation = []

    if dsl:
        result = validate_mermaid(dsl)
        if result["success"]:
            new_documentation.append(
                {
                    "type": "data_models",
                    "explanation": explanation,
                    "code": dsl,
                    "valid": True,
                }
            )
        else:
            warning_msg = (
                f"\n\n> [!WARNING]\n> Failed to validate ERD "
                f"Mermaid DSL: {result['error']}"
            )
            new_documentation.append(
                {
                    "type": "data_models",
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
