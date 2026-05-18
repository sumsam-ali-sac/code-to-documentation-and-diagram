import os
from typing import List, Optional
from langchain.tools import tool

@tool
def list_directory(path: str) -> List[str]:
    """Lists files and directories in a given path within the target project."""
    try:
        # Ensure we stay within the intended directory if needed (security)
        return os.listdir(path)
    except Exception as e:
        return [f"Error: {str(e)}"]

@tool
def read_file(file_path: str, start_line: int = 1, end_line: Optional[int] = None) -> str:
    """Reads the content of a file. Optionally specify start and end lines."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if end_line:
                return "".join(lines[start_line-1:end_line])
            return "".join(lines[start_line-1:])
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def grep_search(pattern: str, path: str) -> List[str]:
    """Searches for a regex pattern within files in a directory."""
    # Simple implementation using os.walk and regex
    import re
    results = []
    try:
        for root, _, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for i, line in enumerate(f, 1):
                            if re.search(pattern, line):
                                results.append(f"{file_path}:{i}: {line.strip()}")
                except:
                    continue
    except Exception as e:
        return [f"Error: {str(e)}"]
    return results[:50] # Limit results
