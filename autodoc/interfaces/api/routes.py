"""
API routes for the AutoDoc service.
Defines endpoints for triggering and tracking documentation generation.
"""

import logging
import os

from fastapi import APIRouter, BackgroundTasks, HTTPException

from autodoc.application.coordinator import run_coordinator
from autodoc.domain.project import DocumentationResponse, ProjectInput
from autodoc.infrastructure.utils.git_handler import (
    cleanup_repository,
    clone_repository,
)

router = APIRouter()

# Simple in-memory store for status tracking
generation_status = {}

logger = logging.getLogger(__name__)


def process_generation(project_name: str, path: str, git_url: str, branch: str):
    """
    Background task to process documentation generation.

    Args:
        project_name: Name of the project.
        path: Local path to the project (optional if git_url is provided).
        git_url: Git URL of the project (optional).
        branch: Branch to use if cloning.
    """
    repo_path = path
    is_temp_repo = False
    try:
        if git_url:
            repo_path = clone_repository(git_url, branch)
            is_temp_repo = True

        if not repo_path or not os.path.exists(repo_path):
            generation_status[project_name] = {
                "status": "Failed",
                "error": "Invalid project path",
            }
            return

        def on_event(event: str):
            """Callback for real-time event updates."""
            if project_name in generation_status:
                if "events" not in generation_status[project_name]:
                    generation_status[project_name]["events"] = []
                generation_status[project_name]["events"].append(event)

        result = run_coordinator(repo_path, on_event=on_event)
        generation_status[project_name].update(
            {
                "status": "Completed",
                "stack": result.get("stack"),
                "diagrams": result.get("diagram_paths"),
            }
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(
            "Error during documentation generation for %s: %s", project_name, e
        )
        generation_status[project_name] = {"status": "Failed", "error": str(e)}
    finally:
        if is_temp_repo and repo_path:
            cleanup_repository(repo_path)


@router.post("/generate", response_model=DocumentationResponse)
async def generate_documentation(
    project: ProjectInput, background_tasks: BackgroundTasks
):
    """
    Trigger the documentation generation process for a project.
    """
    try:
        if not project.path and not project.git_url:
            raise HTTPException(
                status_code=400, detail="Either path or git_url must be provided."
            )

        generation_status[project.name] = {"status": "In Progress", "events": []}

        background_tasks.add_task(
            process_generation,
            project.name,
            project.path,
            project.git_url,
            project.branch,
        )

        return DocumentationResponse(
            project_name=project.name,
            status="Documentation generation started",
            bundle_url=f"/api/v1/status/{project.name}",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to initiate documentation generation")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/status/{project_name}")
async def get_status(project_name: str):
    """
    Get the status of a documentation generation task.
    """
    if project_name not in generation_status:
        raise HTTPException(
            status_code=404, detail="Project not found or generation not started."
        )
    return generation_status[project_name]
