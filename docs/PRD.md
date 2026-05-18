# PRD: AutoDoc - Agentic Documentation & Diagramming Tool

## Problem Statement
Maintaining accurate, visual, and up-to-date documentation for complex, multi-domain codebases is a significant burden. Manual efforts lead to stale diagrams and fragmented knowledge. Developers need an autonomous system that can "understand" code architecture and generate consistent, hierarchical documentation and diagrams.

## Solution
AutoDoc is an autonomous, agentic platform that uses a Coordinator/Worker pattern (LangGraph) to scan, analyze, and document complex projects. It leverages best-of-breed diagramming tools (Python Diagrams, Mermaid) and Azure OpenAI to produce a structured, searchable, and visual Documentation Bundle.

## User Stories (USTs)

### Core Scanning & Agents
1. **UST-01:** As a developer, I want the system to auto-detect my stack (FastAPI, Next.js, etc.) so I don't have to provide manual configuration.
2. **UST-02:** As an architect, I want the Coordinator to map domain boundaries (Context Mapping) so that documentation is modular.
3. **UST-03:** As a user, I want agents to use surgical tools (read/grep) so that only relevant code is processed, saving costs and context.
4. **UST-04:** As a lead dev, I want the agent to self-correct diagram syntax errors via a validator loop to ensure 100% render success.

### Diagramming & Visualization
5. **UST-05:** As a designer, I want architecture diagrams to use industry-standard icons (AWS, Azure, GCP, K8s) via the Python `diagrams` library.
6. **UST-06:** As a developer, I want Sequence diagrams for all major API flows to understand cross-domain interactions.
7. **UST-07:** As a DBA, I want ERDs that show field types, constraints, and relationships across all system modules./
8. **UST-08:** As a user, I want Mermaid diagrams embedded as text in Markdown for easy version control and GitHub rendering.

### API & Persistence
9. **UST-09:** As an operator, I want an API to trigger scans and poll for status/results for integration with CI/CD.
10. **UST-10:** As a manager, I want to browse a history of previously generated documentation versions stored in a database.
11. **UST-11:** As a security officer, I want authentication and project-level permissions to control who can scan which codebases.
12. **UST-12:** As a power user, I want a CLI tool to run AutoDoc locally without using the web service.

---

## Development Roadmap & Task Backlog

### Phase 1: Agentic Engine & Surgical Tools
- [ ] **Task 1.1:** Refine `list_directory`, `read_file`, and `grep_search` tools with robust error handling and path sanitization.
- [ ] **Task 1.2:** Implement `ContextMapper` logic in the Coordinator to identify sub-modules and domain boundaries.
- [ ] **Task 1.3:** Build advanced LangGraph state management to support long-running agent loops and fanned-out workers.
- [ ] **Task 1.4:** Implement "Incremental Scanning" logic to only re-document changed modules.

### Phase 2: Multi-Engine Diagramming Suite
- [ ] **Task 2.1:** Standardize `ArchitectureWorker` to produce high-fidelity system-level PNGs using Python `diagrams`.
- [ ] **Task 2.2:** Build the `MermaidValidator` API-based check for Sequence and ERD diagrams.
- [ ] **Task 2.3:** Implement a "Diagram Gallery" in the UI to preview all generated visuals.
- [ ] **Task 2.4:** Support custom iconography and styling themes for all diagram engines.

### Phase 3: Data Layer & Persistence (DB)
- [ ] **Task 3.1:** Set up a database (PostgreSQL/SQLAlchemy) to track Projects, Scan Tasks, and Generated Artifacts.
- [ ] **Task 3.2:** Implement "Task Logs" to store agent thought processes and tool calls for debugging.
- [ ] **Task 3.3:** Build a storage service to manage the Documentation Bundles (Local disk or S3-compatible).

### Phase 4: API, UI & Security
- [ ] **Task 4.1:** Build the FastAPI "Task Manager" with background workers (Celery/Redis or BackgroundTasks).
- [ ] **Task 4.2:** Implement JWT-based Authentication and API Key management.
- [ ] **Task 4.3:** Develop the "Documentation Browser" UI to navigate hierarchical module docs.
- [ ] **Task 4.4:** Create a standalone CLI (`autodoc-cli`) for local developers.

---

## Implementation Decisions

### Agentic Orchestration
- **LangGraph** is the core orchestrator. We use `StateGraph` with conditional edges for dynamic worker routing.
- **Azure OpenAI** is the LLM of choice, using `gpt-4-turbo-preview` for complex mapping and `gpt-3.5-turbo` for simple documentation tasks to optimize cost.

### Storage & Persistence
- **Database:** PostgreSQL for metadata.
- **File Storage:** Hierarchical folder structure for Documentation Bundles, serving as a static site.

### API Contract
- `POST /api/v1/scan`: Trigger a new scan.
- `GET /api/v1/scan/{task_id}`: Poll for status.
- `GET /api/v1/projects/{id}/docs`: Retrieve the latest bundle.

## Testing Decisions
- **TDD for Tools:** Every surgical tool must have 100% unit test coverage.
- **Mock LLM:** Use a mock LLM provider for CI/CD to test agent flow logic without incurring API costs.
- **Regression Suite:** A set of "Reference Codebases" (e.g., a sample Django app, a sample Next.js app) to verify end-to-end output quality.

## Out of Scope
- Direct code modification (AutoDoc is read-only).
- Support for non-Git version control systems.
- Real-time diagram collaboration (Diagrams are generated, not manually edited in-app).
