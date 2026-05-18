from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage
from autodoc.core.agents.state import AgentState
from autodoc.core.tools.code_scanner import list_directory, read_file, grep_search
from autodoc.core.engine.validator import validate_and_execute_diagram
from langgraph.prebuilt import create_react_agent
import os
import re

llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview"),
)

ARCHITECTURE_WORKER_SYSTEM_PROMPT = """
You are the Architecture Worker for AutoDoc. Your job is to:
1. Map out the high-level system architecture of the project.
2. Generate a Python script using the `diagrams` library to visualize the architecture.

Example script structure:
```python
from diagrams import Diagram, Cluster
from diagrams.onprem.client import Client
from diagrams.onprem.network import Nginx
from diagrams.programming.framework import FastAPI

with Diagram("System Architecture", show=False, filename="arch_output"):
    client = Client("Browser")
    with Cluster("Web Tier"):
        api = FastAPI("API Service")
    client >> api
```

Output ONLY the Python code for the diagram.
"""

def extract_python_code(text: str) -> str:
    pattern = r"```python\s*(.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL)
    if match: return match.group(1).strip()
    pattern = r"```\s*(.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL)
    if match: return match.group(1).strip()
    return text.strip()

def architecture_worker_node(state: AgentState):
    print(f"--- Architecture Worker Started ---")
    project_path = state["project_path"]
    messages = [SystemMessage(content=ARCHITECTURE_WORKER_SYSTEM_PROMPT)] + list(state["messages"])
    
    agent = create_react_agent(llm, [list_directory, read_file, grep_search])
    response = agent.invoke({"messages": messages})
    
    last_message = response["messages"][-1].content
    code = extract_python_code(last_message)
    
    new_documentation = []
    new_diagram_paths = []
    
    if code and "from diagrams" in code:
        result = validate_and_execute_diagram(code, project_path)
        if result["success"]:
            new_documentation.append("Generated Architecture diagram (Python Diagrams).")
            new_diagram_paths.append(os.path.join(project_path, "arch_output.png"))
        else:
            new_documentation.append(f"Failed to generate Architecture diagram: {result['error']}")
    
    return {
        "messages": response["messages"],
        "documentation": new_documentation,
        "diagram_paths": new_diagram_paths
    }
