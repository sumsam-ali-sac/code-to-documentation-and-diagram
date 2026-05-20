"""
State definitions for the AutoDoc agent system.
Defines the AgentState used by LangGraph to manage coordination between workers.
"""
import operator
from typing import TypedDict, List, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    State representation for the AutoDoc system.
    """
    # The messages in the conversation
    messages: Annotated[Sequence[BaseMessage], add_messages]
    # The path to the project being scanned
    project_path: str
    # The identified language stack
    stack: str
    # A list of specific tasks the coordinator has decided are necessary
    tasks: List[dict]
    # A list of "points of interest" identified by the coordinator
    points_of_interest: Annotated[List[str], operator.add]
    # The generated documentation snippets
    documentation: Annotated[List[str], operator.add]
    # Paths to generated diagrams
    diagram_paths: Annotated[List[str], operator.add]
    # Current worker being engaged
    current_worker: str
    # Any errors encountered during the process
    errors: Annotated[List[str], operator.add]
