import os
import subprocess
import tempfile
from pathlib import Path
from langchain_core.documents import Document

SUPPORTED_EXTENSIONS = (
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".go", ".java", ".rs", ".cpp", ".c",
    ".md", ".yaml", ".yml", ".toml", ".sh"
)

class RepoLoader:

    def __init__(self, repo_url: str):
        self.repo_url = repo_url.strip()

    def load(self) -> list[Document]:
        documents = []
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Clone the repository locally with depth=1 (shallow clone)
                subprocess.run(
                    ["git", "clone", "--depth", "1", self.repo_url, temp_dir],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except Exception as e:
                raise RuntimeError(f"Failed to clone repository: {e}")

            for root, dirs, files in os.walk(temp_dir):
                # Skip .git directory
                if ".git" in dirs:
                    dirs.remove(".git")
                
                for file in files:
                    file_path = Path(root) / file
                    if file_path.suffix in SUPPORTED_EXTENSIONS:
                        try:
                            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                                content = f.read()
                            
                            # Keep Unix-style forward slashes for path consistency
                            rel_path = os.path.relpath(file_path, temp_dir).replace("\\", "/")
                            documents.append(
                                Document(
                                    page_content=content,
                                    metadata={"source": rel_path}
                                )
                            )
                        except Exception:
                            # Skip unreadable or binary files
                            continue
        return documents