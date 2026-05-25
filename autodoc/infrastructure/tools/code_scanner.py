"""
Code scanner tools for the AutoDoc system.
Provides LangChain tools for listing directories, reading files, and searching code.
"""

import os
import re
from typing import List, Optional

from langchain.tools import tool


@tool
def list_directory(path: str) -> List[str]:
    """
    Lists files and directories in a given path within the target project.

    Args:
        path: The path to list.

    Returns:
        A list of file and directory names.
    """
    try:
        # Ensure we stay within the intended directory if needed (security)
        return os.listdir(path)
    except Exception as e:  # pylint: disable=broad-exception-caught
        return [f"Error: {str(e)}"]


@tool
def read_file(
    file_path: str, start_line: int = 1, end_line: Optional[int] = None
) -> str:
    """
    Reads the content of a file. Optionally specify start and end lines.

    Args:
        file_path: The path to the file to read.
        start_line: The line number to start reading from (1-based).
        end_line: The line number to stop reading at.

    Returns:
        The content of the file.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if end_line:
                return "".join(lines[start_line - 1 : end_line])
            return "".join(lines[start_line - 1 :])
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error: {str(e)}"


@tool
def grep_search(pattern: str, path: str) -> List[str]:
    """
    Searches for a regex pattern within files in a directory.

    Args:
        pattern: The regex pattern to search for.
        path: The directory path to search within.

    Returns:
        A list of matching lines with file names and line numbers.
    """
    # Simple implementation using os.walk and regex
    results = []
    try:
        for root, _, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        for i, line in enumerate(f, 1):
                            if re.search(pattern, line):
                                results.append(f"{file_path}:{i}: {line.strip()}")
                except Exception:  # pylint: disable=broad-exception-caught
                    continue
    except Exception as e:  # pylint: disable=broad-exception-caught
        return [f"Error: {str(e)}"]
    return results[:50]  # Limit results
