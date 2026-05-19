import os
import pytest
from unittest.mock import patch, MagicMock
from autodoc.application.workers.class_worker import class_worker_node
from langchain_core.messages import HumanMessage

@patch("autodoc.application.workers.class_worker.create_react_agent")
def test_class_worker_node(mock_create_react_agent):
    # Setup mock
    mock_agent = MagicMock()
    mock_create_react_agent.return_value = mock_agent

    mock_response = {
        "messages": [
            HumanMessage(content="```mermaid\nclassDiagram\n    class Test {}\n```")
        ]
    }
    mock_agent.invoke.return_value = mock_response

    # Run worker
    state = {
        "messages": [],
        "project_path": "test_project_node",
        "stack": "Node.js",
        "tasks": [],
        "points_of_interest": [],
        "documentation": [],
        "diagram_paths": [],
        "current_worker": "",
        "errors": []
    }

    result = class_worker_node(state)

    # Assertions
    assert "documentation" in result
    assert len(result["documentation"]) == 1
    assert "classDiagram" in result["documentation"][0]
