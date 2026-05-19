import os
from autodoc.infrastructure.utils.language_detector import detect_stack

def test_detect_stack_python():
    stack = detect_stack("test_project")
    assert "Python" in stack

def test_detect_stack_node():
    stack = detect_stack("test_project_node")
    assert stack == "Express"

def test_detect_stack_go():
    stack = detect_stack("test_project_go")
    assert stack == "Go"
