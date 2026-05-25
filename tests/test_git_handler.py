import os
import shutil
import unittest
from autodoc.infrastructure.utils.git_handler import clone_repository, cleanup_repository

class TestGitHandler(unittest.TestCase):
    def test_clone_and_cleanup_repository(self):
        # Use a small public repository for testing
        git_url = "https://github.com/octocat/Hello-World.git"

        # Clone, use master branch as octocat/Hello-World uses master
        repo_path = clone_repository(git_url, branch="master")
        self.assertTrue(os.path.exists(repo_path))
        self.assertTrue(os.path.isdir(repo_path))
        self.assertTrue(os.path.exists(os.path.join(repo_path, ".git")))
        self.assertTrue(os.path.exists(os.path.join(repo_path, "README")))

        # Cleanup
        cleanup_repository(repo_path)
        self.assertFalse(os.path.exists(repo_path))

    def test_clone_repository_invalid_url(self):
        with self.assertRaises(Exception):
            clone_repository("https://github.com/invalid/invalid.git")

if __name__ == "__main__":
    unittest.main()
