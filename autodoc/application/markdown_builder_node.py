from autodoc.domain.state import AgentState
import os

def markdown_builder_node(state: AgentState):
    print("--- Markdown Builder Started ---")
    project_path = state["project_path"]
    docs = state.get("documentation", [])

    output_dir = os.path.join(project_path, "generated_docs")
    os.makedirs(output_dir, exist_ok=True)

    # If the documentation is simple (only a few blocks), write to a single file
    if len(docs) <= 2:
        with open(os.path.join(output_dir, "Documentation.md"), "w") as f:
            f.write("# Generated Documentation\n\n")
            for doc in docs:
                f.write(doc + "\n\n")
        return {"messages": []}

    # Otherwise, split by topic based on keywords in the generated text
    arch_docs = [d for d in docs if "Architecture" in d]
    erd_docs = [d for d in docs if "ERD" in d]
    seq_docs = [d for d in docs if "Sequence" in d]
    flow_docs = [d for d in docs if "Flow" in d]
    other_docs = [d for d in docs if not any(kw in d for kw in ["Architecture", "ERD", "Sequence", "Flow"])]

    if arch_docs:
        with open(os.path.join(output_dir, "Architecture.md"), "w") as f:
            f.write("# System Architecture\n\n")
            # If architecture generated an image, link it
            arch_img = os.path.join(project_path, "arch_output.png")
            if os.path.exists(arch_img):
                f.write("![Architecture Diagram](../arch_output.png)\n\n")
            for d in arch_docs: f.write(d + "\n\n")

    if erd_docs:
        with open(os.path.join(output_dir, "Data_Models.md"), "w") as f:
            f.write("# Data Models (ERD)\n\n")
            for d in erd_docs: f.write(d + "\n\n")

    if seq_docs or flow_docs:
        with open(os.path.join(output_dir, "Flows.md"), "w") as f:
            f.write("# Application Flows\n\n")
            for d in seq_docs: f.write(d + "\n\n")
            for d in flow_docs: f.write(d + "\n\n")

    if other_docs:
        with open(os.path.join(output_dir, "Miscellaneous.md"), "w") as f:
            f.write("# Other Documentation\n\n")
            for d in other_docs: f.write(d + "\n\n")

    print(f"Documentation generated in {output_dir}")
    return {"messages": []}
