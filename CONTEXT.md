# Context: AutoDoc

A tool to automatically generate documentation and diagrams from source code using an agentic architecture.

## Glossary

### Coordinator Agent
The high-level orchestrator that scans the codebase structure, identifies points of interest, and delegates specific extraction or generation tasks to **Worker Agents**.

### Worker Agent
Specialized modules or sub-agents responsible for specific documentation or diagramming tasks (e.g., ERD extraction, Sequence diagram generation).

### Diagram Module
The collection of rendering engines used to convert structured data or DSL into visual diagrams. Currently includes `diagrams.mingrammer.com` (Architecture) and `Mermaid` (Sequence, ERD, Flow).

### Mermaid
A JavaScript-based diagramming and charting tool that renders Markdown-inspired text definitions into diagrams. Used for Sequence, ERD, and Flow visualizations.

### Structural Metadata
Descriptive text that explains what a module or folder does, serving as the narrative glue that connects different diagrams together.

### AutoDoc Service
The web service (built with FastAPI and Python) that provides an interface for interacting with the Coordinator and Worker agents.

### Language Detection
The process by which the Coordinator Agent identifies the technology stack (e.g., Next.js, FastAPI, React) of a target codebase before dispatching workers.

### Documentation Bundle
A collection of generated Markdown files and diagrams. Mermaid diagrams are embedded as text blocks, while architecture diagrams are included as rendered image files (PNG/SVG) linked within the Markdown.

### Agent Engine
The underlying orchestration framework (LangGraph) that manages the state, logic, and communication between the Coordinator and Worker agents.

### Surgical Tools
A set of specialized functions (e.g., `read_file`, `grep`, `list_directory`) that agents use to interactively explore and retrieve specific parts of the target codebase.

### Diagram Validator
A process that attempts to execute agent-generated diagram code, captures any errors, and feeds them back to the agent for correction.

### Codebase Access
The mechanism by which the AutoDoc Service retrieves the target source code, supporting both local filesystem paths and remote Git repository URLs.

### Domain, Application, and Infrastructure Layers
The standard DDD (Domain-Driven Design) architectural pattern the repository adheres to for structural integrity.

### Flow Worker
A specialized worker that extracts algorithms and complex business logic into Mermaid flowcharts.

### Markdown Builder
A graph node that intelligently splits generated documentation into separate `.md` files based on complexity instead of a single output blob.
