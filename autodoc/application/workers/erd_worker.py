"""
ERD worker module for AutoDoc.
Analyzes database models and relationships, generating Mermaid Entity Relationship Diagrams.
"""
import os
import re

from langchain_core.messages import SystemMessage
from langchain_openai import AzureChatOpenAI
from langgraph.prebuilt import create_react_agent

from autodoc.domain.state import AgentState
from autodoc.infrastructure.engine.validator import validate_mermaid
from autodoc.infrastructure.tools.code_scanner import (grep_search,
                                                       list_directory,
                                                       read_file)

llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview"),
)

ERD_WORKER_SYSTEM_PROMPT = """
You are the ERD Worker for AutoDoc. Your job is to:
1. Identify database models and their relationships in the project.
2. Generate Mermaid DSL for an Entity Relationship Diagram (ERD).

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


def extract_mermaid_code(text: str) -> str:
    """
    Extracts Mermaid code from the LLM response.

    Args:
        text: The raw text response.

    Returns:
        The extracted Mermaid DSL.
    """
    pattern = r"```mermaid\s*(.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    pattern = r"```\s*(.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def erd_worker_node(state: AgentState):
    """
    ERD worker node that generates entity relationship diagrams.

    Args:
        state: The current agent state.

    Returns:
        Updated state with documentation.
    """
    print("--- ERD Worker Started ---")
    messages = [SystemMessage(content=ERD_WORKER_SYSTEM_PROMPT)] + list(state["messages"])

    agent = create_react_agent(llm, [list_directory, read_file, grep_search])
    response = agent.invoke({"messages": messages})

    last_message = response["messages"][-1].content
    dsl = extract_mermaid_code(last_message)

    new_documentation = []

    if dsl:
        result = validate_mermaid(dsl)
        if result["success"]:
            new_documentation.append(f"Generated ERD diagram (Mermaid):\n\n```mermaid\n{dsl}\n```")
        else:
            new_documentation.append(f"Failed to validate ERD Mermaid DSL: {result['error']}")

    return {
        "messages": response["messages"],
        "documentation": new_documentation
    }
