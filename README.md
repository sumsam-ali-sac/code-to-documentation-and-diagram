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

- **Coordinator Agent:** Scans the codebase and delegates tasks.
- **ERD Worker:** Extracts database models and generates ERD diagrams.
- **Diagram Validator:** Executes agent-generated code and handles self-correction.
- **FastAPI:** Provides a web interface for documentation generation.
