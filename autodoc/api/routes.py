from fastapi import APIRouter, HTTPException
from autodoc.schemas.project import ProjectInput, DocumentationResponse
# from autodoc.core.agents.coordinator import run_coordinator

router = APIRouter()

@router.post("/generate", response_model=DocumentationResponse)
async def generate_documentation(project: ProjectInput):
    """
    Trigger the documentation generation process for a project.
    """
    try:
        # result = await run_coordinator(project)
        # return result
        return {
            "project_name": project.name,
            "status": "Documentation generation started (Mock)",
            "bundle_url": f"/bundles/{project.name}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{project_name}")
async def get_status(project_name: str):
    return {"project_name": project_name, "status": "In Progress"}
