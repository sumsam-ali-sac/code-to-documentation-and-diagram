"""
Coordinator module for the AutoDoc system.
Responsible for project analysis and task delegation to specialized workers.
"""

import os
from typing import List

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import AzureChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.types import Send
from pydantic import BaseModel, Field

from autodoc.application.markdown_builder_node import markdown_builder_node
from autodoc.application.workers.architecture_worker import architecture_worker_node
from autodoc.application.workers.base_worker import (
    create_worker_graph,
    run_worker_graph,
)
from autodoc.application.workers.class_worker import class_worker_node
from autodoc.application.workers.erd_worker import erd_worker_node
from autodoc.application.workers.flow_worker import flow_worker_node
from autodoc.application.workers.sequence_worker import sequence_worker_node
from autodoc.domain.state import AgentState
from autodoc.infrastructure.tools.code_scanner import (
    grep_search,
    list_directory,
    read_file,
)
from autodoc.infrastructure.utils.language_detector import detect_stack

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
4. Decide which specialized Worker Agents to engage (architecture, erd, sequence, flow, class).

CRITICAL RULE: You MUST ALWAYS include "architecture_worker" in your task list to provide a high-level system overview.

You must output a JSON block indicating the specific diagramming tasks to run. Use the format:
```json
[
  {"worker": "architecture_worker", "target": "overall system"},
  {"worker": "erd_worker", "target": "database models"},
  {"worker": "sequence_worker", "target": "main API flow"},
  {"worker": "flow_worker", "target": "complex business logic"},
  {"worker": "class_worker", "target": "key classes and interfaces"}
]
```
Choose the other workers that make sense for the project. Output ONLY the valid JSON block as your final answer.
"""


class CoordinatorTask(BaseModel):
    """Structured output for a single task."""

    worker: str = Field(
        description="The name of the worker agent (e.g., architecture_worker)"
    )
    target: str = Field(
        default="", description="The target component or area to document"
    )


class CoordinatorTasks(BaseModel):
    """Structured output for the list of tasks."""

    tasks: List[CoordinatorTask] = Field(
        description="List of tasks for the worker agents"
    )


def coordinator_node(state: AgentState, config=None):
    """
    Coordinator node that analyzes the project and selects tasks.

    Args:
        state: The current agent state.
        config: Runnable configuration.

    Returns:
        Updated state with selected tasks and stack.
    """
    print("--- Coordinator Started ---")
    project_path = state["project_path"]
    stack = detect_stack(project_path)
    # Extract project_name from config if available for callbacks
    on_event = config.get("configurable", {}).get("on_event") if config else None

    events = []
    messages = [SystemMessage(content=COORDINATOR_SYSTEM_PROMPT)] + list(
        state["messages"]
    )
    agent = create_worker_graph(llm, coordinator_tools, COORDINATOR_SYSTEM_PROMPT)

    final_response, events = run_worker_graph(agent, messages, "Coordinator", on_event)

    # Use structured output to reliably extract the tasks from the conversation history
    extractor = llm.with_structured_output(CoordinatorTasks)
    try:
        extraction_result = extractor.invoke(final_response["messages"])
        tasks = [task.model_dump() for task in extraction_result.tasks]
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Extraction failed: {e}")
        tasks = [
            {"worker": "architecture_worker"},
            {"worker": "erd_worker"},
            {"worker": "sequence_worker"},
            {"worker": "flow_worker"},
            {"worker": "class_worker"},
        ]
    print(f"Coordinator selected tasks: {tasks}")

    return {
        "messages": final_response["messages"],
        "stack": stack,
        "tasks": tasks,
        "events": events,
    }


def route_tasks(state: AgentState):
    """
    Routes tasks to the appropriate workers.

    Args:
        state: The current agent state.

    Returns:
        A list of Send objects or a list with the next node name.
    """
    tasks = state.get("tasks", [])
    sends = []
    worker_names = [
        "architecture_worker",
        "erd_worker",
        "sequence_worker",
        "flow_worker",
        "class_worker",
    ]
    for task in tasks:
        worker_name = task.get("worker")
        if worker_name in worker_names:
            sends.append(Send(worker_name, state))
    if not sends:
        return ["markdown_builder"]
    return sends


def run_coordinator(project_path: str, on_event=None):
    """
    Initializes and runs the coordinator workflow.

    Args:
        project_path: Path to the project to document.
        on_event: Optional callback for real-time event streaming.

    Returns:
        The final state of the workflow.
    """
    workflow = StateGraph(AgentState)

    workflow.add_node("coordinator", coordinator_node)
    workflow.add_node("architecture_worker", architecture_worker_node)
    workflow.add_node("erd_worker", erd_worker_node)
    workflow.add_node("sequence_worker", sequence_worker_node)
    workflow.add_node("flow_worker", flow_worker_node)
    workflow.add_node("class_worker", class_worker_node)
    workflow.add_node("markdown_builder", markdown_builder_node)

    workflow.set_entry_point("coordinator")

    # Fan-out to workers in parallel
    workflow.add_conditional_edges(
        "coordinator",
        route_tasks,
        [
            "architecture_worker",
            "erd_worker",
            "sequence_worker",
            "flow_worker",
            "class_worker",
            "markdown_builder",
        ],
    )

    # Fan-in to markdown builder
    workflow.add_edge("architecture_worker", "markdown_builder")
    workflow.add_edge("erd_worker", "markdown_builder")
    workflow.add_edge("sequence_worker", "markdown_builder")
    workflow.add_edge("flow_worker", "markdown_builder")
    workflow.add_edge("class_worker", "markdown_builder")
    workflow.add_edge("markdown_builder", END)

    workflow_app = workflow.compile()

    initial_state = {
        "messages": [
            HumanMessage(content=f"Please document the project at {project_path}")
        ],
        "project_path": project_path,
        "stack": "",
        "points_of_interest": [],
        "documentation": [],
        "diagram_paths": [],
        "events": [],
        "current_worker": "",
        "errors": [],
    }

    return workflow_app.invoke(
        initial_state, config={"configurable": {"on_event": on_event}}
    )
