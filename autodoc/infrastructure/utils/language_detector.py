"""
Language and stack detector for the AutoDoc system.
Analyzes project files to identify the technology stack.
"""

import os


def detect_stack(project_path: str) -> str:
    """
    Detects the technology stack of a project based on its files.

    Args:
        project_path: The path to the project to analyze.

    Returns:
        A string representing the detected technology stack.
    """
    # pylint: disable=too-many-return-statements, too-many-branches
    files = os.listdir(project_path)

    if "package.json" in files:
        # Check for Next.js, React, Express
        try:
            package_json_path = os.path.join(project_path, "package.json")
            with open(package_json_path, "r", encoding="utf-8") as f:
                content = f.read()
                if '"next"' in content:
                    return "Next.js"
                if '"react"' in content:
                    return "React"
                if '"express"' in content:
                    return "Express"
        except Exception:  # pylint: disable=broad-exception-caught
            pass
        return "Node.js"

    if any(f in files for f in ["requirements.txt", "pyproject.toml", "setup.py"]):
        # Check for FastAPI, Django, Flask
        try:
            for file_name in ["requirements.txt", "pyproject.toml"]:
                file_path = os.path.join(project_path, file_name)
                if os.path.exists(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if "fastapi" in content.lower():
                            return "Python (FastAPI)"
                        if "django" in content.lower():
                            return "Python (Django)"
                        if "flask" in content.lower():
                            return "Python (Flask)"
        except Exception:  # pylint: disable=broad-exception-caught
            pass
        return "Python"

    if "go.mod" in files:
        return "Go"

    # Check for Java
    if "pom.xml" in files or "build.gradle" in files:
        return "Java"

    return "Unknown"
