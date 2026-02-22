"""
Storyteller Agent - OpenAI-powered narrative agent for the murder mystery.
"""

import os
from typing import List, Dict, Any, Optional

from openai import OpenAI

from mystery.story import (
    STORYTELLER_SYSTEM_PROMPT,
    PHASE_PROMPTS,
    RESOLUTION_CORRECT,
    RESOLUTION_WRONG,
)


class StorytellerAgent:
    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
        self.conversation_history: List[Dict[str, str]] = []
        self.model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    def _chat_completion(self, system: str, messages: List[Dict[str, str]], max_tokens: int) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system}, *messages],
            max_completion_tokens=max_tokens,
        )
        return (response.choices[0].message.content or "").strip()

    def narrate_intro(self) -> str:
        """Generate the opening narration."""
        system = STORYTELLER_SYSTEM_PROMPT + "\n\n" + PHASE_PROMPTS["scene_setting"]

        text = self._chat_completion(
            system=system,
            messages=[{
                "role": "user",
                "content": (
                    "The detective has just arrived at the crime scene. "
                    "Set the scene in 2-3 sentences. Be dramatic and noir. "
                    "Mention the rain, the restaurant, the victim. "
                    "End by telling the detective to start investigating."
                ),
            }],
            max_tokens=300,
        )

        self.conversation_history.append({"role": "assistant", "content": text})
        return text

    def narrate_discovery(
        self,
        sql_query: str,
        query_results: List[Dict[str, Any]],
        clues_found: List[str],
        new_clues: List[str],
        turn_number: int,
        total_turns: int,
    ) -> str:
        """Narrate what the detective discovers from the query results."""
        phase = self._get_phase(turn_number)
        system = STORYTELLER_SYSTEM_PROMPT + "\n\n" + PHASE_PROMPTS.get(phase, "")

        # Format results for the prompt
        if query_results:
            results_str = "\n".join(str(row) for row in query_results[:15])
        else:
            results_str = "(empty result set)"

        user_msg = (
            f"Turn {turn_number}/{total_turns}. Phase: {phase}.\n\n"
            f"The detective ran this SQL query:\n```sql\n{sql_query}\n```\n\n"
            f"Query returned {len(query_results)} rows:\n{results_str}\n\n"
            f"New clues discovered this turn: {new_clues if new_clues else 'none'}\n"
            f"All clues found so far: {clues_found}\n"
            f"Clues remaining: {8 - len(clues_found)}\n\n"
            f"Narrate what the detective discovers in 2-3 sentences. "
            f"Be dramatic and noir. Reference specific data from the results."
        )

        self.conversation_history.append({"role": "user", "content": user_msg})

        text = self._chat_completion(
            system=system,
            messages=self.conversation_history,
            max_tokens=250,
        )
        self.conversation_history.append({"role": "assistant", "content": text})

        # Keep conversation history manageable
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-16:]

        return text

    def get_hint(self, undiscovered_hints: List[str], turn_number: int) -> str:
        """Generate a contextual hint."""
        if not undiscovered_hints:
            return "You've found all the clues. Time to make your accusation."

        system = STORYTELLER_SYSTEM_PROMPT

        return self._chat_completion(
            system=system,
            messages=[{
                "role": "user",
                "content": (
                    f"Turn {turn_number}. The detective is stuck. "
                    f"Give a subtle in-character hint. The next clue hint is: '{undiscovered_hints[0]}'. "
                    f"Rephrase it as something the detective might think or notice, "
                    f"without being too direct. Keep it to 1-2 sentences."
                ),
            }],
            max_tokens=150,
        )

    def deliver_resolution(self, accusation: str, is_correct: bool, clues_found: List[str]) -> str:
        """Deliver the final resolution narration."""
        if is_correct:
            return RESOLUTION_CORRECT
        else:
            return RESOLUTION_WRONG

    def _get_phase(self, turn_number: int) -> str:
        if turn_number <= 2:
            return "scene_setting"
        elif turn_number <= 6:
            return "investigation"
        elif turn_number <= 9:
            return "closing_in"
        else:
            return "resolution"
