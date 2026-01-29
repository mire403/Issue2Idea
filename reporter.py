from __future__ import annotations

from typing import Any, Dict, List

from .demand_extractor import DemandAnalysis


def _format_overview(overview: List[str]) -> str:
    if not overview:
        return "No overview generated."
    lines = [f"- {item}" for item in overview]
    return "\n".join(lines)


def _format_pain_points(pain_points: List[Dict[str, Any]]) -> str:
    if not pain_points:
        return "_No major pain points identified._"
    blocks: List[str] = []
    for pp in pain_points:
        numbers = ", ".join(str(n) for n in pp.get("evidence_issue_numbers") or [])
        blocks.append(
            "\n".join(
                [
                    f"### {pp.get('id', '')} — {pp.get('summary', '').strip()}",
                    f"- **Priority**: {pp.get('priority', '')}",
                    f"- **Evidence Issues**: {numbers or 'N/A'}",
                    "",
                    pp.get("why_it_matters", "").strip() or "_No rationale provided._",
                ]
            )
        )
    return "\n\n".join(blocks)


def _format_feature_requests(features: List[Dict[str, Any]]) -> str:
    if not features:
        return "_No merged feature requests generated._"
    blocks: List[str] = []
    for fr in features:
        related_pp = ", ".join(fr.get("related_pain_point_ids") or [])
        notes = fr.get("notes", "").strip()
        blocks.append(
            "\n".join(
                [
                    f"### {fr.get('id', '')} — {fr.get('summary', '').strip()}",
                    f"- **Priority**: {fr.get('priority', '')}",
                    f"- **Related Pain Points**: {related_pp or 'N/A'}",
                    "",
                    notes or "_No additional notes._",
                ]
            )
        )
    return "\n\n".join(blocks)


def _format_roadmap(roadmap: List[Dict[str, Any]]) -> str:
    if not roadmap:
        return "_No roadmap suggested._"
    lines: List[str] = []
    sorted_items = sorted(roadmap, key=lambda x: x.get("step", 0))
    for step in sorted_items:
        fr_ids = ", ".join(step.get("related_feature_request_ids") or [])
        lines.append(
            "\n".join(
                [
                    f"### Step {step.get('step', '?')}: {step.get('title', '').strip()}",
                    f"- **Feature Requests**: {fr_ids or 'N/A'}",
                    "",
                    step.get("rationale", "").strip() or "_No rationale provided._",
                ]
            )
        )
    return "\n\n".join(lines)


def render_markdown_report(
    repo_url: str,
    issue_count: int,
    analysis: DemandAnalysis,
) -> str:
    """
    Turn the structured DemandAnalysis into a human-readable Markdown report.
    """
    overview_md = _format_overview(analysis.raw_overview)
    pain_points_md = _format_pain_points(analysis.pain_points)
    features_md = _format_feature_requests(analysis.merged_feature_requests)
    roadmap_md = _format_roadmap(analysis.roadmap)

    return (
        f"## Overview\n\n"
        f"- **Repository**: {repo_url}\n"
        f"- **Analyzed Issues**: {issue_count}\n"
        f"\n"
        f"{overview_md}\n\n"
        f"## Top User Pain Points\n\n"
        f"{pain_points_md}\n\n"
        f"## Feature Requests (Merged)\n\n"
        f"{features_md}\n\n"
        f"## Suggested Roadmap\n\n"
        f"{roadmap_md}\n"
    )

