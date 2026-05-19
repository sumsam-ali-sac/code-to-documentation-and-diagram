import os
from fastapi import APIRouter, HTTPException, BackgroundTasks
from autodoc.domain.project import ProjectInput, DocumentationResponse
from autodoc.application.coordinator import run_coordinator
from autodoc.infrastructure.utils.git_handler import clone_repository, cleanup_repository

router = APIRouter()

# Simple in-memory store for status tracking
generation_status = {}

def process_generation(project_name: str, path: str, git_url: str, branch: str):
    repo_path = path
    is_temp_repo = False
    try:
        if git_url:
            repo_path = clone_repository(git_url, branch)
            is_temp_repo = True

        if not repo_path or not os.path.exists(repo_path):
            generation_status[project_name] = {"status": "Failed", "error": "Invalid project path"}
            return

        result = run_coordinator(repo_path)
        generation_status[project_name] = {
            "status": "Completed",
            "stack": result.get("stack"),
            "diagrams": result.get("diagram_paths")
        }
    except Exception as e:
        generation_status[project_name] = {"status": "Failed", "error": str(e)}
    finally:
        if is_temp_repo and repo_path:
            cleanup_repository(repo_path)

@router.post("/generate", response_model=DocumentationResponse)
async def generate_documentation(project: ProjectInput, background_tasks: BackgroundTasks):
    """
    Trigger the documentation generation process for a project.
    """
    try:
        if not project.path and not project.git_url:
            raise HTTPException(status_code=400, detail="Either path or git_url must be provided.")

        generation_status[project.name] = {"status": "In Progress"}

        background_tasks.add_task(
            process_generation,
            project.name,
            project.path,
            project.git_url,
            project.branch
        )

        return DocumentationResponse(
            project_name=project.name,
            status="Documentation generation started",
            bundle_url=f"/api/v1/status/{project.name}"
        )
    except Exception as e:
        if not isinstance(e, HTTPException):
            raise HTTPException(status_code=500, detail=str(e))
        raise e

@router.get("/status/{project_name}")
async def get_status(project_name: str):
    if project_name not in generation_status:
        raise HTTPException(status_code=404, detail="Project not found or generation not started.")
    return generation_status[project_name]
