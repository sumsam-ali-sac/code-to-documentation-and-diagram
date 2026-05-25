import os
from unittest.mock import patch, MagicMock
from autodoc.application.workers.class_worker import class_worker_node
from langchain_core.messages import HumanMessage

from autodoc.application.workers.architecture_worker import architecture_worker_node

@patch("autodoc.application.workers.architecture_worker.create_worker_graph")
@patch("autodoc.application.workers.architecture_worker.run_worker_graph")
@patch("autodoc.application.workers.architecture_worker.validate_and_execute_diagram")
def test_architecture_worker_node(mock_validate, mock_run, mock_create):
    # Setup mocks
    mock_agent = MagicMock()
    mock_create.return_value = mock_agent
    
    mock_response = {
        "messages": [
            HumanMessage(content="Here is the diagram:\n```python\nfrom diagrams import Diagram\n```")
        ]
    }
    mock_run.return_value = (mock_response, [])
    
    mock_validate.return_value = {"success": True, "error": None}

    # Run worker
    state = {
        "messages": [],
        "project_path": "test_project",
        "documentation": [],
        "diagram_paths": []
    }

    result = architecture_worker_node(state)

    # Assertions
    assert len(result["documentation"]) == 1
    assert result["documentation"][0]["type"] == "architecture"
    assert "from diagrams" in result["documentation"][0]["code"]
    assert len(result["diagram_paths"]) == 1
    assert "arch_output.png" in result["diagram_paths"][0]

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
