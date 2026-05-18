from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from autodoc.core.agents.state import AgentState
from autodoc.core.tools.code_scanner import list_directory, read_file, grep_search
from autodoc.utils.language_detector import detect_stack
from autodoc.core.agents.workers.erd_worker import erd_worker_node
from autodoc.core.agents.workers.architecture_worker import architecture_worker_node
from autodoc.core.agents.workers.sequence_worker import sequence_worker_node
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, END
import os

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
4. Decide which specialized Worker Agents to engage.

Use your tools to explore the codebase surgically.
"""

def coordinator_node(state: AgentState):
    print("--- Coordinator Started ---")
    project_path = state["project_path"]
    stack = detect_stack(project_path)
    
    messages = [SystemMessage(content=COORDINATOR_SYSTEM_PROMPT)] + list(state["messages"])
    agent = create_react_agent(llm, coordinator_tools)
    response = agent.invoke({"messages": messages})
    
    return {
        "messages": response["messages"],
        "stack": stack,
        "current_worker": "all" 
    }

def run_coordinator(project_path: str):
    workflow = StateGraph(AgentState)
    
    workflow.add_node("coordinator", coordinator_node)
    workflow.add_node("architecture_worker", architecture_worker_node)
    workflow.add_node("erd_worker", erd_worker_node)
    workflow.add_node("sequence_worker", sequence_worker_node)
    
    workflow.set_entry_point("coordinator")
    
    # Fan-out to workers in parallel
    workflow.add_edge("coordinator", "architecture_worker")
    workflow.add_edge("coordinator", "erd_worker")
    workflow.add_edge("coordinator", "sequence_worker")
    
    # Fan-in to END
    workflow.add_edge("architecture_worker", END)
    workflow.add_edge("erd_worker", END)
    workflow.add_edge("sequence_worker", END)
    
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
