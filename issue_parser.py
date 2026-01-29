from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

from .github_client import Issue, IssueComment


@dataclass
class IssueText:
    """Flattened textual representation of an Issue for LLM consumption."""

    number: int
    title: str
    body: str
    comments: List[str]
    url: str
    state: str

    def to_prompt_block(self) -> str:
        comments_block = ""
        if self.comments:
            comments_joined = "\n---\n".join(self.comments)
            comments_block = f"\nComments:\n{comments_joined}"
        return (
            f"Issue #{self.number}: {self.title}\n"
            f"State: {self.state}\n"
            f"URL: {self.url}\n"
            f"Body:\n{self.body or '(no body)'}"
            f"{comments_block}"
        )


def issue_to_text(issue: Issue) -> IssueText:
    comments: List[str] = []
    if issue.comments:
        for c in issue.comments:
            # Keep concise metadata but focus on actual text
            prefix = f"@{c.user}: " if getattr(c, "user", None) else ""
            comments.append(f"{prefix}{c.body}")
    return IssueText(
        number=issue.number,
        title=issue.title or "",
        body=issue.body or "",
        comments=comments,
        url=issue.html_url,
        state=issue.state,
    )


def bulk_issues_to_text(issues: Iterable[Issue]) -> List[IssueText]:
    return [issue_to_text(i) for i in issues]

