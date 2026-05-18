from pydantic import BaseModel, Field
from typing import Optional, List

class ProjectInput(BaseModel):
    name: str = Field(..., description="The name of the project")
    path: Optional[str] = Field(None, description="Local path to the codebase")
    git_url: Optional[str] = Field(None, description="Remote Git URL to the codebase")
    branch: str = Field("main", description="Branch to scan")

class DocumentationResponse(BaseModel):
    project_name: str
    status: str
    bundle_url: Optional[str] = None
    errors: Optional[List[str]] = None
