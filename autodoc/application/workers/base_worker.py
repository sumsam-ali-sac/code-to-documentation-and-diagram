"""
Base worker module providing a transparent, custom LangGraph implementation
for tool-calling agents.
"""

from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, SystemMessage, ToolMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field


class WorkerState(TypedDict):
    """State specific to the worker graph."""

    messages: Annotated[Sequence[BaseMessage], add_messages]


class WorkerDiagramResult(BaseModel):
    """Structured output for the diagram result."""

    code: str = Field(description="The diagram code (Mermaid or Python).")
    explanation: str = Field(
        description="A detailed markdown explanation of what this diagram represents, "
        "its components, and the flow or architecture it describes."
    )


def create_worker_graph(llm, tools, system_prompt: str):
    """
    Creates a custom tool-calling StateGraph for a worker.

    Args:
        llm: The language model instance.
        tools: List of tools to bind to the LLM.
        system_prompt: The system prompt for the worker.

    Returns:
        A compiled LangGraph app representing the worker.
    """
    # Bind tools to the LLM
    llm_with_tools = llm.bind_tools(tools)

    # Node: LLM Call
    def call_model(state: WorkerState):
        messages = state["messages"]
        # Ensure system prompt is the first message if not present
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=system_prompt)] + list(messages)
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    # Node: Tools
    tool_node = ToolNode(tools)

    # Edge: conditional routing after LLM call
    def should_continue(state: WorkerState):
        messages = state["messages"]
        last_message = messages[-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END

    # Build the graph
    workflow = StateGraph(WorkerState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)

    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", should_continue, ["tools", END])
    workflow.add_edge("tools", "agent")

    return workflow.compile()


def run_worker_graph(agent, messages, worker_name: str, on_event=None):
    """
    Executes the worker graph and collects events.
    """
    events = []
    final_response = None

    for chunk in agent.stream({"messages": messages}, stream_mode="values"):
        final_response = chunk
        last_msg = chunk["messages"][-1]

        if isinstance(last_msg, AIMessage) and last_msg.tool_calls:
            for tc in last_msg.tool_calls:
                reason = last_msg.content[:100]
                event_str = (
                    f"[{worker_name}] Reasoning: {reason}... Calling tool: {tc['name']}"
                )
                events.append(event_str)
                if on_event:
                    on_event(event_str)
                print(event_str)
        elif isinstance(last_msg, ToolMessage):
            content_str = str(last_msg.content)[:100]
            event_str = (
                f"[{worker_name}] Tool '{last_msg.name}' returned: {content_str}..."
            )
            events.append(event_str)
            if on_event:
                on_event(event_str)
            print(event_str)

    return final_response, events


def extract_diagram_result(llm, messages: Sequence[BaseMessage]):
    """Extracts a structured diagram result from the LLM messages."""
    extractor = llm.with_structured_output(WorkerDiagramResult)
    try:
        extraction_result = extractor.invoke(messages)
        return extraction_result.code, extraction_result.explanation
    except (ValueError, TypeError, KeyError) as e:
        print(f"Extraction failed: {e}")
        return "", "Diagram generation failed."
