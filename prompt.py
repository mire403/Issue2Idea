from __future__ import annotations

from textwrap import dedent


SYSTEM_PROMPT = dedent(
    """
    You are a senior product manager and user research expert.
    Your task is to read GitHub Issues and extract the **real user needs and pain points**,
    not just the literal feature requests.

    You must:
    - Identify what users are truly struggling with or trying to achieve.
    - Group semantically similar needs into merged, higher-level demands.
    - Assess the impact and urgency for each demand and assign a priority:
      - High   = critical pain / frequent / blocking many users
      - Medium = important but not blocking, or affects fewer users
      - Low    = nice-to-have, minor improvement, or edge case

    Be concrete, avoid vague product language, and stay close to actual user wording.
    Answer in Markdown using the exact JSON structure requested in the user prompt.
    """
).strip()


def build_user_prompt(issue_blocks: str) -> str:
    """
    Build the user message for the LLM.

    The model is instructed to output a JSON object embedded in Markdown,
    so that it's easy to parse while still being human-readable.
    """
    return dedent(
        f"""
        You are given a set of GitHub Issues (titles, bodies, and comments).

        Read all the issues carefully and then produce:

        1. A short overview (2–4 bullet points) describing what users are struggling with overall.
        2. A list of **top user pain points** – distilled, non-duplicated problems.
        3. A set of **merged feature requests / opportunities** derived from those pain points.
        4. A suggested **implementation roadmap** ordered by priority.

        Use the following JSON schema for your final answer (wrap it in a Markdown code block):

        ```json
        {{
          "overview": [
            "string"
          ],
          "pain_points": [
            {{
              "id": "pp_1",
              "summary": "short human-friendly description of the pain point",
              "evidence_issue_numbers": [1, 2, 5],
              "why_it_matters": "why this pain is important from user/product perspective",
              "priority": "High | Medium | Low"
            }}
          ],
          "merged_feature_requests": [
            {{
              "id": "fr_1",
              "summary": "merged feature / solution idea that addresses one or more pain points",
              "related_pain_point_ids": ["pp_1", "pp_3"],
              "priority": "High | Medium | Low",
              "notes": "implementation hints or constraints if present in issues"
            }}
          ],
          "roadmap": [
            {{
              "step": 1,
              "title": "short phase title",
              "related_feature_request_ids": ["fr_1", "fr_2"],
              "rationale": "why this step comes at this stage"
            }}
          ]
        }}
        ```

        - Make sure `priority` is always exactly one of: `High`, `Medium`, `Low`.
        - Reuse `pain_points` across `merged_feature_requests` and `roadmap` by IDs.
        - Focus on **user value**, not internal technical refactors unless explicitly requested by users.

        Here are the GitHub Issues (one by one):

        ---
        {issue_blocks}
        ---

        Now, produce the JSON as specified above, wrapped in a Markdown ```json code block.
        """
    ).strip()

