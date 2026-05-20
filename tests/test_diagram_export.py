import os
import shutil
import unittest
from autodoc.infrastructure.engine.validator import download_mermaid_png
from autodoc.application.markdown_builder_node import _process_diagrams

class TestDiagramExport(unittest.TestCase):
    def test_download_mermaid_png(self):
        # Simple class diagram
        dsl = "classDiagram\n    class Test {}"
        output_path = "test_diagram.png"

        # Ensure clean state
        if os.path.exists(output_path):
            os.remove(output_path)

        success = download_mermaid_png(dsl, output_path)

        self.assertTrue(success)
        self.assertTrue(os.path.exists(output_path))
        self.assertGreater(os.path.getsize(output_path), 0)

        # Cleanup
        if os.path.exists(output_path):
            os.remove(output_path)

    def test_process_diagrams(self):
        project_path = "test_temp_project"
        if os.path.exists(project_path):
            shutil.rmtree(project_path)
        os.makedirs(project_path)

        docs = [
            "Some text before\n```mermaid\nclassDiagram\n    class A\n```\nSome text after",
            "Another one\n```mermaid\nerDiagram\n    B ||--o{ C : uses\n```"
        ]

        updated_docs = _process_diagrams(project_path, docs)

        # Check updated docs
        self.assertIn("![Classes Diagram](../diagrams/classes.png)", updated_docs[0])
        self.assertIn("![Data_models Diagram](../diagrams/data_models.png)", updated_docs[1])
        self.assertNotIn("```mermaid", updated_docs[0])
        self.assertNotIn("```mermaid", updated_docs[1])

        # Check files
        diagrams_dir = os.path.join(project_path, "diagrams")
        mermaid_dir = os.path.join(diagrams_dir, "mermaid")

        self.assertTrue(os.path.exists(os.path.join(diagrams_dir, "classes.png")))
        self.assertTrue(os.path.exists(os.path.join(diagrams_dir, "data_models.png")))
        self.assertTrue(os.path.exists(os.path.join(mermaid_dir, "classes.md")))
        self.assertTrue(os.path.exists(os.path.join(mermaid_dir, "data_models.md")))

        # Verify content of mermaid MD
        with open(os.path.join(mermaid_dir, "classes.md"), "r") as f:
            content = f.read()
            self.assertIn("classDiagram", content)

        # Cleanup
        shutil.rmtree(project_path)

if __name__ == "__main__":
    unittest.main()
