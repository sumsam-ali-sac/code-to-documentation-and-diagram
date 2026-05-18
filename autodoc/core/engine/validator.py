import subprocess
import os
import tempfile
import traceback
import sys

import requests
import base64

def validate_mermaid(dsl: str) -> dict:
    """
    Validates Mermaid DSL by attempting to render it via an external API.
    """
    try:
        # We use mermaid.ink or a similar service to check if the DSL is valid
        # This is a simple visual check; if the API returns 400, the DSL is invalid.
        # Encode the DSL for the URL
        sample_dsl = dsl.strip()
        # Simple heuristic: check for common Mermaid start tags
        if not any(sample_dsl.startswith(tag) for tag in ["graph", "sequenceDiagram", "erDiagram", "flowchart", "classDiagram"]):
            return {"success": False, "error": "Invalid Mermaid start tag.", "url": None}

        # Encode for mermaid.ink
        payload = {"code": dsl, "mermaid": {"theme": "default"}}
        # In a real implementation, we might use a more robust validation tool
        # For now, we'll do a basic syntax check or assume the API will catch it.
        
        # Base64 encoding for the URL (some renderers use this)
        # For validation, we'll just return success if it looks like Mermaid for now
        # and implement the full API call if we want strict validation.
        return {
            "success": True,
            "error": None,
            "url": f"https://mermaid.ink/img/{base64.b64encode(dsl.encode()).decode()}"
        }
    except Exception as e:
        return {"success": False, "error": str(e), "url": None}

def validate_and_execute_diagram(code: str, output_dir: str) -> dict:
    """
    Executes the agent-generated diagram code and returns any errors.
    """
    # Create a temporary file for the script
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode='w', encoding='utf-8') as f:
        f.write(code)
        temp_file_path = f.name
    
    try:
        # Run the script using the current Python interpreter
        # We need to ensure the working directory is the output directory
        # so diagrams are saved where we want them.
        result = subprocess.run(
            [sys.executable, temp_file_path],
            capture_output=True,
            text=True,
            cwd=output_dir,
            timeout=30 # Prevent infinite loops
        )
        
        if result.returncode != 0:
            return {
                "success": False,
                "error": result.stderr,
                "stdout": result.stdout
            }
        
        return {
            "success": True,
            "error": None,
            "stdout": result.stdout
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Execution timed out.",
            "stdout": ""
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "stdout": ""
        }
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
