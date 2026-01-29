from __future__ import annotations

import dataclasses
import re
from typing import Any, Dict, Iterable, List, Optional

import requests


GITHUB_API_BASE = "https://api.github.com"


@dataclasses.dataclass
class IssueComment:
    id: int
    body: str
    user: Optional[str] = None


@dataclasses.dataclass
class Issue:
    id: int
    number: int
    title: str
    body: str
    state: str
    html_url: str
    user: Optional[str] = None
    comments: List[IssueComment] | None = None


class GitHubClient:
    """Lightweight wrapper for GitHub REST API used in this project."""

    def __init__(
        self,
        token: Optional[str] = None,
        base_url: str = GITHUB_API_BASE,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()
        headers: Dict[str, str] = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "demandlens/0.1.0",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self.session.headers.update(headers)

    @staticmethod
    def parse_repo_url(repo_url: str) -> tuple[str, str]:
        """
        Parse a GitHub repository URL and return (owner, repo).

        Supports forms like:
        - https://github.com/owner/repo
        - https://github.com/owner/repo/
        - git@github.com:owner/repo.git
        """
        url = repo_url.strip()

        # SSH form: git@github.com:owner/repo.git
        ssh_match = re.match(r"git@github.com:(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$", url)
        if ssh_match:
            return ssh_match.group("owner"), ssh_match.group("repo")

        # HTTPS form
        https_match = re.match(
            r"https?://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?/?$",
            url,
        )
        if https_match:
            return https_match.group("owner"), https_match.group("repo")

        raise ValueError(f"Unsupported GitHub repo URL: {repo_url!r}")

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"
        resp = self.session.get(url, params=params, timeout=30)
        if resp.status_code >= 400:
            raise RuntimeError(
                f"GitHub API error {resp.status_code} for {url}: {resp.text[:500]}"
            )
        return resp.json()

    def list_issues(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        max_issues: int = 100,
        include_pull_requests: bool = False,
    ) -> List[Issue]:
        """
        List issues for a repository (optionally excluding PRs).

        GitHub's /issues endpoint returns both issues and pull requests.
        """
        issues: List[Issue] = []
        per_page = 100
        page = 1

        while len(issues) < max_issues:
            params = {
                "state": state,
                "per_page": min(per_page, max_issues - len(issues)),
                "page": page,
                "sort": "created",
                "direction": "desc",
            }
            data = self._get(f"repos/{owner}/{repo}/issues", params=params)
            if not data:
                break

            for item in data:
                # PRs have "pull_request" field; skip by default
                if not include_pull_requests and "pull_request" in item:
                    continue
                issues.append(
                    Issue(
                        id=item["id"],
                        number=item["number"],
                        title=item.get("title") or "",
                        body=item.get("body") or "",
                        state=item.get("state") or "",
                        html_url=item.get("html_url") or "",
                        user=(item.get("user") or {}).get("login"),
                        comments=[],
                    )
                )
                if len(issues) >= max_issues:
                    break

            if len(data) < per_page:
                break
            page += 1

        return issues

    def fetch_comments_for_issues(
        self,
        owner: str,
        repo: str,
        issues: Iterable[Issue],
    ) -> List[Issue]:
        """Populate comments for the given issues."""
        for issue in issues:
            if getattr(issue, "number", None) is None:
                continue
            comments_data = self._get(
                f"repos/{owner}/{repo}/issues/{issue.number}/comments",
                params={"per_page": 100},
            )
            comments: List[IssueComment] = []
            for c in comments_data:
                comments.append(
                    IssueComment(
                        id=c["id"],
                        body=c.get("body") or "",
                        user=(c.get("user") or {}).get("login"),
                    )
                )
            issue.comments = comments
        return list(issues)

