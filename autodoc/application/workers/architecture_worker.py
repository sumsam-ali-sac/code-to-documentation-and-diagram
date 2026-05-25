"""
Architecture worker module for AutoDoc.
Analyzes project structure and generates system architecture diagrams using the diagrams library.
"""

import glob
import os
import shutil
import tempfile

from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI

from autodoc.application.workers.base_worker import (
    create_worker_graph,
    extract_diagram_result,
    run_worker_graph,
)
from autodoc.domain.state import AgentState
from autodoc.infrastructure.engine.validator import validate_and_execute_diagram
from autodoc.infrastructure.tools.code_scanner import grep_search, read_file

llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview"),
)


@tool
def search_diagram_icons(query: str) -> str:
    """
    Searches the local icon library for a given technology or generic name.
    Returns the absolute paths of matching .png files.
    """
    # Find the autodoc/assets/icons directory relative to this file
    base_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    icons_dir = os.path.join(base_dir, "assets", "icons")

    if not os.path.exists(icons_dir):
        return "Icon library directory not found."

    matches = []
    search_query = query.lower()
    for root, _, files in os.walk(icons_dir):
        for file in files:
            if file.endswith(".png") and search_query in file.lower():
                matches.append(os.path.join(root, file))

    if not matches:
        return f"No icons found for '{query}'. Please use standard built-in diagrams nodes instead."

    return "\n".join(matches[:15])


ARCHITECTURE_WORKER_SYSTEM_PROMPT = """
You are the Architecture Worker for AutoDoc. Your job is to:
1. Map out the high-level system architecture of the project.
2. Generate a Python script using the `diagrams` library to visualize the architecture.
3. IMPORTANT: The `diagrams` library uses specific import paths. DO NOT hallucinate imports.
   Use generic fallback nodes like `diagrams.custom.Custom` if you are unsure, or stick ONLY to these common verified imports:
   - `diagrams.onprem.database.PostgreSQL`, `diagrams.onprem.database.MySQL`
   - `diagrams.programming.framework.FastAPI`, `diagrams.programming.framework.Django`
   - `diagrams.onprem.client.Client`, `diagrams.onprem.client.Users`
   - `diagrams.onprem.network.Nginx`, `diagrams.onprem.network.Internet`

4. CUSTOM ICONS SUPPORT: 
   - You MUST use the `search_diagram_icons` tool to find the exact absolute paths to local `.png` icons for specific technologies (e.g., 'fastapi', 'react', 'postgres', 'aws', 'azure').
   - When you find a suitable icon path, use it with the `Custom` node:
     ```python
     from diagrams.custom import Custom
     api = Custom("Service Name", "C:\\absolute\\path\\to\\icon.png")
     ```
   - If `search_diagram_icons` returns nothing, fall back to standard built-in nodes.

Example script structure:
```python
from diagrams import Diagram, Cluster
from diagrams.onprem.client import Client
from diagrams.programming.framework import FastAPI
from diagrams.onprem.database import PostgreSQL

with Diagram("System Architecture", show=False, filename="arch_output"):
    client = Client("Browser")
    with Cluster("Web Tier"):
        api = FastAPI("API Service")
        db = PostgreSQL("Database")
        api >> db
    client >> api
```

Output ONLY the Python code for the diagram.
"""


def architecture_worker_node(state: AgentState, config=None):
    """
    Architecture worker node that generates system diagrams.

    Args:
        state: The current agent state.
        config: Runnable configuration.

    Returns:
        Updated state with documentation and diagram paths.
    """
    print("--- Architecture Worker Started ---")
    project_path = state["project_path"]
    on_event = config.get("configurable", {}).get("on_event") if config else None
    messages = [SystemMessage(content=ARCHITECTURE_WORKER_SYSTEM_PROMPT)] + list(
        state["messages"]
    )

    # Use specialized search_diagram_icons instead of list_directory for efficiency
    agent = create_worker_graph(
        llm,
        [search_diagram_icons, read_file, grep_search],
        ARCHITECTURE_WORKER_SYSTEM_PROMPT,
    )

    final_response, events = run_worker_graph(
        agent, messages, "ArchitectureWorker", on_event
    )

    code, explanation = extract_diagram_result(llm, final_response["messages"])

    new_documentation = []
    new_diagram_paths = []

    if code and "from diagrams" in code:
        # Execute in a temporary directory to reliably capture the output PNG
        with tempfile.TemporaryDirectory() as temp_dir:
            result = validate_and_execute_diagram(code, temp_dir)
            if result["success"]:
                # Find the generated PNG file
                png_files = glob.glob(os.path.join(temp_dir, "*.png"))
                if png_files:
                    generated_png = png_files[0]
                    diagrams_dir = os.path.join(project_path, "diagrams")
                    os.makedirs(diagrams_dir, exist_ok=True)
                    final_arch_path = os.path.join(diagrams_dir, "architecture.png")
                    shutil.copy(generated_png, final_arch_path)

                    new_documentation.append(
                        {
                            "type": "architecture",
                            "explanation": explanation,
                            "code": code,
                            "valid": True,
                        }
                    )
                    new_diagram_paths.append(final_arch_path)
            else:
                warning_msg = (
                    f"\n\n> [!WARNING]\n> Failed to generate Architecture "
                    f"diagram: {result['error']}"
                )
                new_documentation.append(
                    {
                        "type": "architecture",
                        "explanation": explanation + warning_msg,
                        "code": "",
                        "valid": False,
                    }
                )

    return {
        "messages": final_response["messages"],
        "documentation": new_documentation,
        "diagram_paths": new_diagram_paths,
        "events": events,
    }
