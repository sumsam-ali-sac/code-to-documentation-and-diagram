import os
import shutil
import unittest
from unittest.mock import patch, MagicMock
from autodoc.application.markdown_builder_node import markdown_builder_node

class TestDiagramExport(unittest.TestCase):
    @patch("autodoc.application.markdown_builder_node.download_mermaid_png")
    def test_markdown_builder_node(self, mock_download):
        # Mock download to create a dummy file
        def side_effect(dsl, path):
            with open(path, "wb") as f:
                f.write(b"dummy mermaid png")
            return True
        mock_download.side_effect = side_effect
        
        project_path = "test_temp_project"
        if os.path.exists(project_path):
            shutil.rmtree(project_path)
        os.makedirs(project_path)

        # Create a dummy architecture.png in diagrams folder to simulate new architecture worker behavior
        diagrams_dir = os.path.join(project_path, "diagrams")
        os.makedirs(diagrams_dir, exist_ok=True)
        with open(os.path.join(diagrams_dir, "architecture.png"), "wb") as f:
            f.write(b"dummy image data")

        state = {
            "project_path": project_path,
            "documentation": [
                {
                    "type": "architecture",
                    "explanation": "This is the system architecture.",
                    "code": "from diagrams import Diagram\nwith Diagram('test'): pass",
                    "valid": True
                },
                {
                    "type": "classes",
                    "explanation": "This is the class diagram.",
                    "code": "classDiagram\n    class Test {}",
                    "valid": True
                }
            ]
        }

        # Run the builder
        markdown_builder_node(state)

        # Check files
        output_dir = os.path.join(project_path, "generated_docs")
        diagrams_dir = os.path.join(project_path, "diagrams")
        mermaid_dir = os.path.join(diagrams_dir, "mermaid")

        self.assertTrue(os.path.exists(os.path.join(output_dir, "Architecture.md")))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "Classes.md")))
        self.assertTrue(os.path.exists(os.path.join(diagrams_dir, "architecture.png")))
        self.assertTrue(os.path.exists(os.path.join(diagrams_dir, "classes_1.png")))
        self.assertTrue(os.path.exists(os.path.join(mermaid_dir, "classes_1.md")))

        # Verify content of Architecture MD
        with open(os.path.join(output_dir, "Architecture.md"), "r") as f:
            content = f.read()
            self.assertIn("# Architecture Documentation", content)
            self.assertIn("![Architecture Diagram](../diagrams/architecture.png)", content)
            self.assertIn("This is the system architecture.", content)

        # Cleanup
        shutil.rmtree(project_path)

if __name__ == "__main__":
    unittest.main()
