"""Game state tracking."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class GameState:
    turn_number: int = 0
    max_turns: int = 10
    clues_found: List[str] = field(default_factory=list)
    query_history: List[Dict] = field(default_factory=list)
    total_score: float = 0.0
    hints_used: int = 0
    accusation: Optional[str] = None
    game_over: bool = False
    sql_concepts_used: List[str] = field(default_factory=list)

    @property
    def current_phase(self) -> str:
        if self.turn_number <= 2:
            return "scene_setting"
        elif self.turn_number <= 6:
            return "investigation"
        elif self.turn_number <= 9:
            return "closing_in"
        else:
            return "resolution"

    @property
    def clue_progress(self) -> float:
        return len(self.clues_found) / 8

    @property
    def turns_remaining(self) -> int:
        return max(0, self.max_turns - self.turn_number)

    def record_query(self, sql: str, clues: List[str], concepts: List[str]):
        self.query_history.append({
            "turn": self.turn_number,
            "sql": sql,
            "clues_found": clues,
        })
        for concept in concepts:
            if concept not in self.sql_concepts_used:
                self.sql_concepts_used.append(concept)
