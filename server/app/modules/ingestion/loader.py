from langchain_community.document_loaders import GithubFileLoader
from langchain_core.documents import Document

SUPPORTED_EXTENSIONS = (
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".go", ".java", ".rs", ".cpp", ".c",
    ".md", ".yaml", ".yml", ".toml", ".sh"
)

class RepoLoader:

    def __init__(self, repo_url: str):
        self.repo = self._extract_repo(repo_url)

    def _extract_repo(self, url: str) -> str:
        # extracts "owner/repo" from full github url
        return url.replace("https://github.com/", "").strip("/")

    def load(self) -> list[Document]:
        loader = GithubFileLoader(
            repo=self.repo,
            access_token="",
            github_api_url="https://api.github.com",
            file_filter=lambda path: path.endswith(SUPPORTED_EXTENSIONS)
        )
        return loader.load()