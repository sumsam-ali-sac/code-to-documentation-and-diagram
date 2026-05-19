import os

def detect_stack(project_path: str) -> str:
    """
    Detects the technology stack of a project based on its files.
    """
    files = os.listdir(project_path)
    
    if "package.json" in files:
        # Check for Next.js, React, Express
        try:
            with open(os.path.join(project_path, "package.json"), "r") as f:
                content = f.read()
                if '"next"' in content:
                    return "Next.js"
                if '"react"' in content:
                    return "React"
                if '"express"' in content:
                    return "Express"
        except:
            pass
        return "Node.js"
    
    if "requirements.txt" in files or "pyproject.toml" in files or "setup.py" in files:
        # Check for FastAPI, Django, Flask
        try:
            for file_name in ["requirements.txt", "pyproject.toml"]:
                file_path = os.path.join(project_path, file_name)
                if os.path.exists(file_path):
                    with open(file_path, "r") as f:
                        content = f.read()
                        if "fastapi" in content.lower():
                            return "Python (FastAPI)"
                        if "django" in content.lower():
                            return "Python (Django)"
                        if "flask" in content.lower():
                            return "Python (Flask)"
        except:
            pass
        return "Python"
        
    if "go.mod" in files:
        return "Go"
        
    # Check for Java
    if "pom.xml" in files or "build.gradle" in files:
        return "Java"

    return "Unknown"
