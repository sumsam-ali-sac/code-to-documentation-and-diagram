# AutoDoc

Automatic documentation and diagram generation using LangGraph and Python Diagrams.

## Prerequisites

- **Python 3.10+**
- **PDM** (Dependency Management)
- **Graphviz** (Required by the `diagrams` library)
- **Azure OpenAI Account**

## Setup

1.  **Clone the repository.**
2.  **Install dependencies:**
    ```bash
    pdm install
    ```
3.  **Configure environment variables:**
    Create a `.env` file in the root directory:
    ```env
    AZURE_OPENAI_API_KEY=your_api_key
    AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
    AZURE_OPENAI_API_VERSION=2023-12-01-preview
    AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
    ```

## Usage

### Running the API
```bash
pdm run python -m autodoc.main
```

### Running the Test Script
```bash
pdm run python run_test.py
```

## Architecture

- **Domain-Driven Design:** The codebase is split cleanly into `domain`, `application`, and `infrastructure` layers.
- **Coordinator Agent:** Scans the codebase, dynamically decides necessary diagrams, and routes tasks using the LangGraph Send API.
- **Workers:** Specialized agents (`Architecture`, `ERD`, `Sequence`, `Flow`) that execute diagram generation concurrently.
- **Diagram Validator:** Executes agent-generated code and handles self-correction.
- **Markdown Builder:** Analyzes generated documentation complexity and splits it into structured `.md` files (e.g., `Architecture.md`, `Data_Models.md`).
- **FastAPI:** Provides a web interface for documentation generation.
