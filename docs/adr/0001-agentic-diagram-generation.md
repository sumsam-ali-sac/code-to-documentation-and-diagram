# ADR 0001: Agentic Diagram Generation via Direct Code Execution

## Status
Accepted

## Context
The `diagrams` library (diagrams.mingrammer.com) requires Python code to define nodes, clusters, and edges. We need a way for agents to reliably produce these diagrams from their understanding of a target codebase.

## Decision
We will use a **Direct Generation** approach where Worker Agents write Python scripts using the `diagrams` library. These scripts are executed in a controlled environment.

## Rationale
*   **Flexibility:** Agents can use any feature, icon set, or layout option in the library without needing an intermediate mapping layer or DSL.
*   **Self-Correction:** By feeding execution errors back into the agent (the **Diagram Validator** loop), the system can autonomously fix minor syntax or API usage errors.
*   **Simplicity:** Reduces the amount of "glue code" needed to translate between an agent's mental model and the final visual output.

## Consequences
*   **Security:** Execution of agent-generated code requires careful handling to prevent malicious or accidental system damage (e.g., using a separate process or container).
*   **Environment:** The execution environment must have `graphviz` and the `diagrams` library installed.
*   **Error Handling:** We must implement a robust capture of stdout/stderr from the executed scripts to provide high-quality feedback to the agent.
