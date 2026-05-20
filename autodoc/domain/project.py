"""
Domain models for the AutoDoc project.
Defines the input and output structures for the documentation service.
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class ProjectInput(BaseModel):
    """
    Input model for a project documentation request.
    """
    name: str = Field(..., description="The name of the project")
    path: Optional[str] = Field(None, description="Local path to the codebase")
    git_url: Optional[str] = Field(None, description="Remote Git URL to the codebase")
    branch: str = Field("main", description="Branch to scan")


class DocumentationResponse(BaseModel):
    """
    Response model for a documentation generation request.
    """
    project_name: str
    status: str
    bundle_url: Optional[str] = None
    errors: Optional[List[str]] = None
