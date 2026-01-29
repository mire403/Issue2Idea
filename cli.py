from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from tqdm import tqdm

from .demand_extractor import DemandExtractor
from .github_client import GitHubClient
from .issue_parser import bulk_issues_to_text
from .llm import LLMClient
from .reporter import render_markdown_report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="demandlens",
        description="Extract real user demands from GitHub Issues using LLMs.",
    )
    parser.add_argument("repo_url", help="GitHub repository URL, e.g. https://github.com/owner/repo")
    parser.add_argument(
        "--max-issues",
        type=int,
        default=100,
        help="Maximum number of recent issues to fetch (default: 100).",
    )
    parser.add_argument(
        "--state",
        choices=["open", "closed, all"],
        default="open",
        help="Issue state to fetch from GitHub (default: open).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="requirements.md",
        help="Output Markdown file path (default: requirements.md).",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="LLM model name (default: value configured in llm.py).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    # Load environment variables from .env if present
    load_dotenv()

    args = parse_args(argv)

    try:
        owner, repo = GitHubClient.parse_repo_url(args.repo_url)
    except ValueError as exc:
        print(f"[demandlens] Invalid repo URL: {exc}", file=sys.stderr)
        return 1

    github_token = os.getenv("GITHUB_TOKEN")
    client = GitHubClient(token=github_token)

    print(f"[demandlens] Fetching issues from {owner}/{repo} ...")
    issues = client.list_issues(owner, repo, state=args.state, max_issues=args.max_issues)
    issues = client.fetch_comments_for_issues(owner, repo, issues)
    print(f"[demandlens] Retrieved {len(issues)} issues (after PR filtering).")

    issue_texts = bulk_issues_to_text(issues)

    model_name = args.model or "gpt-4.1-mini"
    llm_client = LLMClient(model=model_name)
    extractor = DemandExtractor(llm_client)

    print("[demandlens] Calling LLM to analyze user demands (this may take a while)...")
    analysis = extractor.analyze(issue_texts)

    output_md = render_markdown_report(args.repo_url, len(issue_texts), analysis)
    output_path = Path(args.output)
    output_path.write_text(output_md, encoding="utf-8")
    print(f"[demandlens] Requirements report written to {output_path}")

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

