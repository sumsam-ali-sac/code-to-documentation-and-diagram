"""
Markdown builder node for the AutoDoc system.
Consolidates documentation from all workers and writes it to markdown files.
"""
import os
import re
import shutil
from typing import List, Dict
from autodoc.domain.state import AgentState
from autodoc.infrastructure.engine.validator import download_mermaid_png


def _write_to_file(file_path: str, title: str, docs: List[str], image_link: str = None):
    """
    Helper function to write documentation blocks to a file.

    Args:
        file_path: The path to the file to write.
        title: The title of the documentation section.
        docs: A list of documentation strings.
        image_link: Optional markdown image link.
    """
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        if image_link:
            f.write(f"{image_link}\n\n")
        for doc in docs:
            f.write(doc + "\n\n")


def _process_diagrams(project_path: str, docs: List[str]) -> List[str]:
    """
    Processes documentation strings to extract Mermaid diagrams, save them as PNGs,
    and update the strings with image links.

    Args:
        project_path: The root path of the project.
        docs: A list of documentation strings.

    Returns:
        Updated list of documentation strings.
    """
    diagrams_dir = os.path.join(project_path, "diagrams")
    mermaid_dir = os.path.join(diagrams_dir, "mermaid")
    os.makedirs(mermaid_dir, exist_ok=True)

    updated_docs = []
    mermaid_pattern = r"```mermaid\s*(.*?)\s*```"

    for doc in docs:
        new_doc = doc
        matches = re.finditer(mermaid_pattern, doc, re.DOTALL)
        for match in matches:
            dsl = match.group(1).strip()
            # Determine diagram type for naming
            diag_type = "diagram"
            if "classDiagram" in dsl:
                diag_type = "classes"
            elif "erDiagram" in dsl:
                diag_type = "data_models"
            elif "sequenceDiagram" in dsl:
                diag_type = "sequence"
            elif "graph " in dsl or "flowchart" in dsl:
                diag_type = "flows"

            # Save Mermaid MD
            mermaid_file = os.path.join(mermaid_dir, f"{diag_type}.md")
            with open(mermaid_file, "w", encoding="utf-8") as f:
                f.write(f"```mermaid\n{dsl}\n```")

            # Download PNG
            png_file_name = f"{diag_type}.png"
            png_path = os.path.join(diagrams_dir, png_file_name)
            if download_mermaid_png(dsl, png_path):
                # Replace code block with image link
                # Note: The MD files are in generated_docs/, so the path to diagrams/ is ../diagrams/
                img_link = f"![{diag_type.capitalize()} Diagram](../diagrams/{png_file_name})"
                new_doc = new_doc.replace(match.group(0), img_link)

        updated_docs.append(new_doc)

    return updated_docs


def markdown_builder_node(state: AgentState):
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

    # Process Mermaid diagrams first
    docs = _process_diagrams(project_path, docs)

    output_dir = os.path.join(project_path, "generated_docs")
    diagrams_dir = os.path.join(project_path, "diagrams")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(diagrams_dir, exist_ok=True)

    # Handle Architecture diagram (Python Diagrams)
    arch_img_source = os.path.join(project_path, "arch_output.png")
    arch_img_target = os.path.join(diagrams_dir, "architecture.png")
    arch_img_link = None

    if os.path.exists(arch_img_source):
        shutil.move(arch_img_source, arch_img_target)
        arch_img_link = "![Architecture Diagram](../diagrams/architecture.png)"

    # Categorize documentation
    categories = {
        "Architecture": [d for d in docs if "Architecture" in d],
        "ERD": [d for d in docs if "ERD" in d or "Data_Models" in d or "data_models" in d],
        "Sequence": [d for d in docs if "Sequence" in d or "sequence" in d],
        "Flow": [d for d in docs if "Flow" in d or "flows" in d],
        "Class": [d for d in docs if "Class" in d or "classes" in d],
    }

    keywords = categories.keys()
    other_docs = [d for d in docs if not any(kw in d for kw in keywords)]

    if categories["Architecture"]:
        _write_to_file(
            os.path.join(output_dir, "Architecture.md"),
            "System Architecture",
            categories["Architecture"],
            arch_img_link
        )

    if categories["ERD"]:
        _write_to_file(
            os.path.join(output_dir, "Data_Models.md"),
            "Data Models (ERD)",
            categories["ERD"]
        )

    if categories["Sequence"] or categories["Flow"]:
        _write_to_file(
            os.path.join(output_dir, "Flows.md"),
            "Application Flows",
            categories["Sequence"] + categories["Flow"]
        )

    if categories["Class"]:
        _write_to_file(
            os.path.join(output_dir, "Classes.md"),
            "Class Diagrams",
            categories["Class"]
        )

    if other_docs:
        _write_to_file(
            os.path.join(output_dir, "Miscellaneous.md"),
            "Other Documentation",
            other_docs
        )

    print(f"Documentation generated in {output_dir}")
    print(f"Diagrams saved in {diagrams_dir}")
    return {"messages": []}
