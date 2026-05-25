"""
Markdown builder node for the AutoDoc system.
Consolidates documentation from all workers and writes it to markdown files.
"""

import os
import shutil

from autodoc.domain.state import AgentState
from autodoc.infrastructure.engine.validator import download_mermaid_png


def markdown_builder_node(state: AgentState):
    # pylint: disable=too-many-locals
    """
    Markdown builder node that processes documentation and writes files.

    Args:
        state: The current agent state.

    Returns:
        Empty message list.
    """
    print("--- Markdown Builder Started ---")
    project_path = state["project_path"]
    docs = state.get("documentation", [])

    output_dir = os.path.join(project_path, "generated_docs")
    diagrams_dir = os.path.join(project_path, "diagrams")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(diagrams_dir, exist_ok=True)

    for idx, doc in enumerate(docs):
        # Fallback if somehow a string got through
        if isinstance(doc, str):
            doc = {
                "type": "Miscellaneous",
                "explanation": doc,
                "code": "",
                "valid": True,
            }

        doc_type = doc.get("type", "miscellaneous")
        explanation = doc.get("explanation", "")
        code = doc.get("code", "")
        valid = doc.get("valid", False)

        # Capitalize and format filename
        title = doc_type.replace("_", " ").title()
        md_file = os.path.join(output_dir, f"{title}.md")

        image_link = ""
        if code and valid:
            if doc_type == "architecture":
                # Architecture diagram is already saved as architecture.png in diagrams_dir by the worker
                arch_img_target = os.path.join(diagrams_dir, "architecture.png")
                # Fallback check for old behavior just in case
                arch_img_source = os.path.join(project_path, "arch_output.png")
                if os.path.exists(arch_img_source):
                    shutil.move(arch_img_source, arch_img_target)
                
                if os.path.exists(arch_img_target):
                    image_link = "![Architecture Diagram](../diagrams/architecture.png)"
            else:
                # Handle mermaid
                png_file_name = f"{doc_type}_{idx}.png"
                png_path = os.path.join(diagrams_dir, png_file_name)

                # Save mermaid md
                mermaid_dir = os.path.join(diagrams_dir, "mermaid")
                os.makedirs(mermaid_dir, exist_ok=True)
                with open(
                    os.path.join(mermaid_dir, f"{doc_type}_{idx}.md"),
                    "w",
                    encoding="utf-8",
                ) as f:
                    f.write(f"```mermaid\n{code}\n```")

                if download_mermaid_png(code, png_path):
                    image_link = f"![{title} Diagram](../diagrams/{png_file_name})"

        # Write MD file
        # Append if file already exists
        mode = "a" if os.path.exists(md_file) else "w"
        with open(md_file, mode, encoding="utf-8") as f:
            if mode == "w":
                f.write(f"# {title} Documentation\n\n")
            if image_link:
                f.write(f"{image_link}\n\n")
            if explanation:
                f.write(f"{explanation}\n\n---\n\n")

    print(f"Documentation generated in {output_dir}")
    print(f"Diagrams saved in {diagrams_dir}")
    return {"messages": []}
