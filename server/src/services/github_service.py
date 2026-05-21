import tempfile
import asyncio
import re
import os
from pathlib import Path
from typing import List
import requests
from git import Repo
from github import Github
from src.core.config import config


def _parse_owner_repo_from_url(url: str) -> tuple[str, str]:
    # supports https://github.com/owner/repo(.git) and git@github.com:owner/repo.git
    patterns = [
        r"github\.com[:/]+(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$",
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            owner = m.group("owner")
            repo = m.group("repo")
            return owner, repo
    raise ValueError(f"Unable to parse owner/repo from url: {url}")


class GitHubService:
    @staticmethod
    async def clone_repository_to_temp(repository_url: str) -> str:
        """Clone a public repository to a temporary directory and return the path."""
        temp_dir = tempfile.mkdtemp(prefix="repo_")

        def clone():
            Repo.clone_from(repository_url, temp_dir)
            return temp_dir

        return await asyncio.to_thread(clone)

    @staticmethod
    def _get_client() -> Github:
        token = getattr(config, "github_token", None)
        if token:
            return Github(token)
        return Github()

    @staticmethod
    async def get_readme_text(repository_url: str) -> str:
        owner, repo = _parse_owner_repo_from_url(repository_url)
        g = GitHubService._get_client()

        def fetch():
            gh_repo = g.get_repo(f"{owner}/{repo}")
            try:
                readme = gh_repo.get_readme()
                return readme.decoded_content.decode("utf-8", errors="ignore")
            except Exception:
                return ""

        return await asyncio.to_thread(fetch)

    @staticmethod
    async def list_files(repository_url: str, path: str = "", recursive: bool = True) -> List[str]:
        owner, repo = _parse_owner_repo_from_url(repository_url)
        g = GitHubService._get_client()

        def fetch():
            results: List[str] = []
            gh_repo = g.get_repo(f"{owner}/{repo}")

            def walk(contents, prefix=""):
                for item in contents:
                    if item.type == "dir":
                        if recursive:
                            walk(gh_repo.get_contents(item.path), prefix=prefix)
                    else:
                        results.append(item.path)

            try:
                contents = gh_repo.get_contents(path or "")
                if isinstance(contents, list):
                    walk(contents)
                elif contents:
                    results.append(contents.path)
            except Exception:
                pass

            return results

        return await asyncio.to_thread(fetch)

    @staticmethod
    async def download_archive_to_temp(repository_url: str, ref: str | None = None) -> str:
        """Download the repository zipball for the given ref (or default branch) to a temp dir and extract it, returning path to extracted folder."""
        owner, repo = _parse_owner_repo_from_url(repository_url)
        token = getattr(config, "github_token", None)
        g = GitHubService._get_client()

        def download_and_extract():
            gh_repo = g.get_repo(f"{owner}/{repo}")
            branch = ref or getattr(gh_repo, "default_branch", "main")
            url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"
            headers = {}
            if token:
                headers["Authorization"] = f"token {token}"

            resp = requests.get(url, headers=headers, stream=True, timeout=60)
            resp.raise_for_status()

            temp_dir = tempfile.mkdtemp(prefix="repo_zip_")
            zip_path = os.path.join(temp_dir, "repo.zip")
            with open(zip_path, "wb") as fh:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        fh.write(chunk)

            # extract
            extract_dir = os.path.join(temp_dir, "extracted")
            Path(extract_dir).mkdir(parents=True, exist_ok=True)
            import zipfile

            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(extract_dir)

            # If extraction created a single top-level folder, return that path
            entries = list(Path(extract_dir).iterdir())
            if len(entries) == 1 and entries[0].is_dir():
                return str(entries[0])
            return extract_dir

        return await asyncio.to_thread(download_and_extract)
