"""
Validation engine for the AutoDoc system.
Provides utilities for validating Mermaid DSL and executing diagram generation code.
"""

import base64
import os
import re
import subprocess
import sys
import tempfile
import zlib

import httpx


def clean_mermaid_dsl(dsl: str) -> str:
    """Removes markdown code blocks if present."""
    pattern = r"```(?:mermaid)?\s*(.*?)\s*```"
    match = re.search(pattern, dsl, re.DOTALL)
    if match:
        return match.group(1).strip()
    return dsl.strip()


def validate_mermaid(dsl: str) -> dict:
    """
    Validates Mermaid DSL by checking for common start tags and encoding for Kroki.

    Args:
        dsl: The Mermaid DSL string to validate.

    Returns:
        A dictionary indicating success, error message, and a preview URL.
    """
    try:
        sample_dsl = dsl.strip()
        valid_tags = [
            "graph",
            "sequenceDiagram",
            "erDiagram",
            "flowchart",
            "classDiagram",
        ]
        if not any(sample_dsl.startswith(tag) for tag in valid_tags):
            return {
                "success": False,
                "error": "Invalid Mermaid start tag.",
                "url": None,
            }

        compressed = zlib.compress(dsl.encode("utf-8"), 9)
        encoded_dsl = base64.urlsafe_b64encode(compressed).decode("utf-8")
        return {
            "success": True,
            "error": None,
            "url": f"https://kroki.io/mermaid/svg/{encoded_dsl}",
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        return {"success": False, "error": str(e), "url": None}


def download_mermaid_png(dsl: str, output_path: str) -> bool:
    """
    Downloads a rendered Mermaid PNG from Kroki.

    Args:
        dsl: The Mermaid DSL string.
        output_path: The path to save the PNG file.

    Returns:
        True if successful, False otherwise.
    """
    try:
        url = "https://kroki.io/mermaid/png"
        response = httpx.post(
            url, data=dsl, headers={"Content-Type": "text/plain"}, timeout=20.0
        )

        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            return True
        print(
            f"Error downloading Mermaid PNG: Status {response.status_code}, {response.text}"
        )
        return False
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error downloading Mermaid PNG: {e}")
        return False


def validate_and_execute_diagram(code: str, output_dir: str) -> dict:
    """
    Executes the agent-generated diagram code and returns any errors.

    Args:
        code: The Python code to execute.
        output_dir: The directory where diagrams should be saved.

    Returns:
        A dictionary containing success status, error messages, and stdout.
    """
    # Create a temporary file for the script
    with tempfile.NamedTemporaryFile(
        suffix=".py", delete=False, mode="w", encoding="utf-8"
    ) as f:
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
            timeout=30,  # Prevent infinite loops
            check=False,
        )

        if result.returncode != 0:
            return {"success": False, "error": result.stderr, "stdout": result.stdout}

        return {"success": True, "error": None, "stdout": result.stdout}

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Execution timed out.", "stdout": ""}
    except Exception as e:  # pylint: disable=broad-exception-caught
        return {"success": False, "error": str(e), "stdout": ""}
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
