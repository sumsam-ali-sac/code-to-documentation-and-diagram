from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage
from autodoc.domain.state import AgentState
from autodoc.infrastructure.tools.code_scanner import list_directory, read_file, grep_search
from autodoc.infrastructure.engine.validator import validate_mermaid
from langgraph.prebuilt import create_react_agent
import os
import re

llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview"),
)

CLASS_WORKER_SYSTEM_PROMPT = """
You are the Class Worker for AutoDoc. Your job is to:
1. Identify the key classes, interfaces, and their methods/attributes in the project.
2. Generate Mermaid DSL for a Class Diagram.

Example Mermaid Class Diagram:
```mermaid
classDiagram
    class Animal {
        +int age
        +String gender
        +isMammal()
        +mate()
    }
    class Duck {
        +String beakColor
        +swim()
        +quack()
    }
    class Fish {
        -int sizeInFt
        -canEat()
    }
    Animal <|-- Duck
    Animal <|-- Fish
```

Focus on the relationships between classes (inheritance, composition, etc.).
Output ONLY the Mermaid DSL code block.
"""

def extract_mermaid_code(text: str) -> str:
    pattern = r"```mermaid\s*(.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL)
    if match: return match.group(1).strip()
    pattern = r"```\s*(.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL)
    if match: return match.group(1).strip()
    return text.strip()

def class_worker_node(state: AgentState):
    """
    The class worker node that extracts classes/objects and generates Mermaid DSL.
    """
    print("--- Class Worker Started ---")
    messages = [
        SystemMessage(content=CLASS_WORKER_SYSTEM_PROMPT),
    ] + list(state["messages"])

    agent = create_react_agent(llm, [list_directory, read_file, grep_search])
    response = agent.invoke({"messages": messages})

    last_message = response["messages"][-1].content
    dsl = extract_mermaid_code(last_message)

    new_documentation = []

    if dsl:
        result = validate_mermaid(dsl)
        if result["success"]:
            new_documentation.append(f"Generated Class diagram (Mermaid):\n\n```mermaid\n{dsl}\n```")
        else:
            new_documentation.append(f"Failed to validate Class Mermaid DSL: {result['error']}")

    return {
        "messages": response["messages"],
        "documentation": new_documentation
    }
