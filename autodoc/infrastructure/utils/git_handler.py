"""
Git utility for the AutoDoc system.
Provides functions for cloning and cleaning up remote repositories.
"""
import os
import shutil
import tempfile
import git


def clone_repository(git_url: str, branch: str = "main") -> str:
    """
    Clones a remote git repository to a temporary directory.

    Args:
        git_url: The URL of the repository to clone.
        branch: The branch to clone.

    Returns:
        The path to the cloned repository.

    Raises:
        RuntimeError: If cloning fails.
    """
    temp_dir = tempfile.mkdtemp(prefix="autodoc_repo_")
    try:
        git.Repo.clone_from(git_url, temp_dir, branch=branch, env={'GIT_TERMINAL_PROMPT': '0'})
        return temp_dir
    except Exception as e:
        # Clean up if clone fails
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        raise RuntimeError(f"Failed to clone repository: {str(e)}") from e


def cleanup_repository(repo_path: str):
    """
    Cleans up the cloned repository directory.

    Args:
        repo_path: The path to the directory to remove.
    """
    if repo_path and os.path.exists(repo_path) and repo_path.startswith(tempfile.gettempdir()):
        shutil.rmtree(repo_path, ignore_errors=True)
