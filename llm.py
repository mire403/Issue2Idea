from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, Optional

from openai import OpenAI


class LLMClient:
    """
    Thin wrapper around OpenAI's Chat Completions API.

    This abstraction exists so that you can swap out the backend later
    (e.g. to Azure OpenAI, local models, etc.) without touching the rest
    of the codebase.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4.1-mini",
        base_url: Optional[str] = None,
    ) -> None:
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Please set it in your environment or .env file."
            )

        client_kwargs: Dict[str, Any] = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url

        self._client = OpenAI(**client_kwargs)
        self.model = model

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        content = resp.choices[0].message.content or ""
        return content

    @staticmethod
    def extract_json_from_markdown(markdown_text: str) -> Dict[str, Any]:
        """
        Extract the first JSON object from a Markdown string that may contain ```json blocks.
        """
        # Look for ```json ... ``` first
        code_block_match = re.search(
            r"```json\s*(\{.*?\})\s*```", markdown_text, flags=re.DOTALL | re.IGNORECASE
        )
        raw = code_block_match.group(1) if code_block_match else markdown_text

        # Fallback: try to find first {...} JSON object if parsing fails
        try:
            return json.loads(raw)
        except Exception:
            brace_match = re.search(r"(\{.*\})", markdown_text, flags=re.DOTALL)
            if brace_match:
                try:
                    return json.loads(brace_match.group(1))
                except Exception as exc:  # pragma: no cover - best-effort parsing
                    raise ValueError(f"Failed to parse JSON from LLM output: {exc}") from exc
            raise ValueError("No JSON object found in LLM output.")

