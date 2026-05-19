from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from autodoc.domain.state import AgentState
from autodoc.infrastructure.tools.code_scanner import list_directory, read_file, grep_search
from autodoc.infrastructure.utils.language_detector import detect_stack
from autodoc.application.workers.erd_worker import erd_worker_node
from autodoc.application.workers.architecture_worker import architecture_worker_node
from autodoc.application.workers.sequence_worker import sequence_worker_node
from autodoc.application.workers.flow_worker import flow_worker_node
from autodoc.application.markdown_builder_node import markdown_builder_node
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, END
from langgraph.types import Send
import os
import json

# Initialize the Azure OpenAI LLM
llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview"),
)

coordinator_tools = [list_directory, read_file, grep_search]

COORDINATOR_SYSTEM_PROMPT = """
You are the Coordinator Agent for AutoDoc. Your job is to:
1. Scan the root of the project to identify the technology stack.
2. Map out the high-level project structure.
3. Identify "Points of Interest" (Database models, API definitions, Business logic).
4. Decide which specialized Worker Agents to engage (architecture, erd, sequence, flow).

You must output a JSON block indicating the specific diagramming tasks to run. Use the format:
```json
[
  {"worker": "architecture_worker", "target": "overall system"},
  {"worker": "erd_worker", "target": "database models"},
  {"worker": "sequence_worker", "target": "main API flow"},
  {"worker": "flow_worker", "target": "complex business logic"}
]
```
Choose the workers that make sense for the project. Output ONLY the valid JSON block as your final answer.
"""

def extract_json_tasks(text: str) -> list:
    import re
    pattern = r"```json\s*(.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except:
            pass
    try:
        return json.loads(text)
    except:
        return [{"worker": "architecture_worker"}, {"worker": "erd_worker"}, {"worker": "sequence_worker"}, {"worker": "flow_worker"}]

def coordinator_node(state: AgentState):
    print("--- Coordinator Started ---")
    project_path = state["project_path"]
    stack = detect_stack(project_path)

    messages = [SystemMessage(content=COORDINATOR_SYSTEM_PROMPT)] + list(state["messages"])
    agent = create_react_agent(llm, coordinator_tools)
    response = agent.invoke({"messages": messages})

    last_message = response["messages"][-1].content
    tasks = extract_json_tasks(last_message)
    print(f"Coordinator selected tasks: {tasks}")

    return {
        "messages": response["messages"],
        "stack": stack,
        "tasks": tasks
    }

def route_tasks(state: AgentState):
    tasks = state.get("tasks", [])
    sends = []
    for task in tasks:
        worker_name = task.get("worker")
        if worker_name in ["architecture_worker", "erd_worker", "sequence_worker", "flow_worker"]:
            sends.append(Send(worker_name, state))
    if not sends:
        return ["markdown_builder"]
    return sends

def run_coordinator(project_path: str):
    workflow = StateGraph(AgentState)

    workflow.add_node("coordinator", coordinator_node)
    workflow.add_node("architecture_worker", architecture_worker_node)
    workflow.add_node("erd_worker", erd_worker_node)
    workflow.add_node("sequence_worker", sequence_worker_node)
    workflow.add_node("flow_worker", flow_worker_node)
    workflow.add_node("markdown_builder", markdown_builder_node)

    workflow.set_entry_point("coordinator")

    # Fan-out to workers in parallel
    workflow.add_conditional_edges("coordinator", route_tasks, ["architecture_worker", "erd_worker", "sequence_worker", "flow_worker", "markdown_builder"])

    # Fan-in to markdown builder
    workflow.add_edge("architecture_worker", "markdown_builder")
    workflow.add_edge("erd_worker", "markdown_builder")
    workflow.add_edge("sequence_worker", "markdown_builder")
    workflow.add_edge("flow_worker", "markdown_builder")
    workflow.add_edge("markdown_builder", END)

    app = workflow.compile()

    initial_state = {
        "messages": [HumanMessage(content=f"Please document the project at {project_path}")],
        "project_path": project_path,
        "stack": "",
        "points_of_interest": [],
        "documentation": [],
        "diagram_paths": [],
        "current_worker": "",
        "errors": []
    }

    return app.invoke(initial_state)
