from typing import TypedDict, List, Annotated, Sequence
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    # The messages in the conversation
    messages: Annotated[Sequence[BaseMessage], operator.add]
    # The path to the project being scanned
    project_path: str
    # The identified language stack
    stack: str
    # A list of "points of interest" identified by the coordinator
    points_of_interest: List[str]
    # The generated documentation snippets
    documentation: List[str]
    # Paths to generated diagrams
    diagram_paths: List[str]
    # Current worker being engaged
    current_worker: str
    # Any errors encountered during the process
    errors: List[str]
