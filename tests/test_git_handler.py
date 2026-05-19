import os
import pytest
from autodoc.infrastructure.utils.git_handler import clone_repository, cleanup_repository

def test_clone_and_cleanup_repository():
    # Use a small public repository for testing
    git_url = "https://github.com/octocat/Hello-World.git"

    # Clone, use master branch as octocat/Hello-World uses master
    repo_path = clone_repository(git_url, branch="master")
    assert os.path.exists(repo_path)
    assert os.path.isdir(repo_path)
    assert os.path.exists(os.path.join(repo_path, ".git"))
    assert os.path.exists(os.path.join(repo_path, "README"))

    # Cleanup
    cleanup_repository(repo_path)
    assert not os.path.exists(repo_path)

def test_clone_repository_invalid_url():
    with pytest.raises(Exception):
        clone_repository("https://github.com/invalid/invalid.git")
