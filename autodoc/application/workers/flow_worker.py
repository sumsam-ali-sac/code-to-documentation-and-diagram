from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage
from autodoc.domain.state import AgentState
from autodoc.infrastructure.tools.code_scanner import list_directory, read_file, grep_search
from langgraph.prebuilt import create_react_agent
import os

llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview"),
)

FLOW_WORKER_SYSTEM_PROMPT = """
You are the Flow Worker for AutoDoc. Your job is to:
1. Identify key business logic flows or algorithms in the project.
2. Generate Mermaid DSL for a flowchart diagram.

Example Mermaid Flowchart:
```mermaid
graph TD
    A[Start] --> B{Is it valid?}
    B -- Yes --> C[Process]
    B -- No --> D[Reject]
    C --> E[End]
    D --> E
```

Focus on the internal logic of complex functions or processes.
Output ONLY the Mermaid DSL code block.
"""

from autodoc.infrastructure.engine.validator import validate_mermaid
import re

def extract_mermaid_code(text: str) -> str:
    pattern = r"```mermaid\s*(.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL)
    if match: return match.group(1).strip()
    pattern = r"```\s*(.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL)
    if match: return match.group(1).strip()
    return text.strip()

def flow_worker_node(state: AgentState):
    """
    The flow worker node that extracts logic algorithms and generates Mermaid flowcharts.
    """
    print("--- Flow Worker Started ---")
    messages = [
        SystemMessage(content=FLOW_WORKER_SYSTEM_PROMPT),
    ] + list(state["messages"])

    agent = create_react_agent(llm, [list_directory, read_file, grep_search])
    response = agent.invoke({"messages": messages})

    last_message = response["messages"][-1].content
    dsl = extract_mermaid_code(last_message)

    new_documentation = []

    if dsl:
        result = validate_mermaid(dsl)
        if result["success"]:
            new_documentation.append(f"Generated Flow diagram (Mermaid):\n\n```mermaid\n{dsl}\n```")
        else:
            new_documentation.append(f"Failed to validate Flow Mermaid DSL: {result['error']}")

    return {
        "messages": response["messages"],
        "documentation": new_documentation
    }
