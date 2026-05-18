from typing import TypedDict, List, Annotated, Sequence
from langchain_core.messages import BaseMessage
import operator
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # The messages in the conversation
    messages: Annotated[Sequence[BaseMessage], add_messages]
    # The path to the project being scanned
    project_path: str
    # The identified language stack
    stack: str
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
