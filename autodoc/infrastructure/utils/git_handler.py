import os
import shutil
import tempfile
import git

def clone_repository(git_url: str, branch: str = "main") -> str:
    """
    Clones a remote git repository to a temporary directory.
    Returns the path to the cloned repository.
    """
    temp_dir = tempfile.mkdtemp(prefix="autodoc_repo_")
    try:
        git.Repo.clone_from(git_url, temp_dir, branch=branch, env={'GIT_TERMINAL_PROMPT': '0'})
        return temp_dir
    except Exception as e:
        # Clean up if clone fails
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        raise Exception(f"Failed to clone repository: {str(e)}")

def cleanup_repository(repo_path: str):
    """
    Cleans up the cloned repository directory.
    """
    if repo_path and os.path.exists(repo_path) and repo_path.startswith(tempfile.gettempdir()):
        shutil.rmtree(repo_path, ignore_errors=True)
