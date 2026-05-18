import os

def detect_stack(project_path: str) -> str:
    """
    Detects the technology stack of a project based on its files.
    """
    files = os.listdir(project_path)
    
    if "package.json" in files:
        # Check for Next.js or React
        with open(os.path.join(project_path, "package.json"), "r") as f:
            content = f.read()
            if '"next"' in content:
                return "Next.js"
            if '"react"' in content:
                return "React"
        return "Node.js"
    
    if "requirements.txt" in files or "pyproject.toml" in files or "setup.py" in files:
        # Check for FastAPI, Django, Flask
        # This is a simple heuristic; a real version would scan the dependencies
        return "Python"
        
    if "go.mod" in files:
        return "Go"
        
    return "Unknown"
