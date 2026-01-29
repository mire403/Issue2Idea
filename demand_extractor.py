from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List

from .issue_parser import IssueText
from .llm import LLMClient
from .prompt import SYSTEM_PROMPT, build_user_prompt


@dataclass
class DemandAnalysis:
    raw_overview: List[str]
    pain_points: List[Dict[str, Any]]
    merged_feature_requests: List[Dict[str, Any]]
    roadmap: List[Dict[str, Any]]
    raw_json: Dict[str, Any]


class DemandExtractor:
    """
    Orchestrates the interaction with the LLM to extract user demands
    from a set of GitHub Issues.
    """

    def __init__(self, llm_client: LLMClient) -> None:
        self._llm = llm_client

    def analyze(self, issues: Iterable[IssueText]) -> DemandAnalysis:
        # Concatenate issues into a single long prompt block.
        blocks = [issue.to_prompt_block() for issue in issues]
        issue_blocks = "\n\n====================\n\n".join(blocks)

        user_prompt = build_user_prompt(issue_blocks)
        llm_output = self._llm.chat(SYSTEM_PROMPT, user_prompt)
        data = self._llm.extract_json_from_markdown(llm_output)

        overview = list(data.get("overview") or [])
        pain_points = list(data.get("pain_points") or [])
        merged_feature_requests = list(data.get("merged_feature_requests") or [])
        roadmap = list(data.get("roadmap") or [])

        return DemandAnalysis(
            raw_overview=overview,
            pain_points=pain_points,
            merged_feature_requests=merged_feature_requests,
            roadmap=roadmap,
            raw_json=data,
        )

