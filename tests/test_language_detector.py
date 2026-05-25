import os
import unittest
from autodoc.infrastructure.utils.language_detector import detect_stack

class TestLanguageDetector(unittest.TestCase):
    def test_detect_stack_python(self):
        stack = detect_stack("test_project")
        self.assertIn("Python", stack)

    def test_detect_stack_node(self):
        stack = detect_stack("test_project_node")
        self.assertEqual(stack, "Express")

    def test_detect_stack_go(self):
        stack = detect_stack("test_project_go")
        self.assertEqual(stack, "Go")

if __name__ == "__main__":
    unittest.main()
