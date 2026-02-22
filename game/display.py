"""CLI display with ANSI colors and formatting."""

import sys
import time
from typing import List, Dict, Any

from game.state import GameState


class Display:
    # ANSI color codes
    NOIR = "\033[90m"       # dark gray
    GOLD = "\033[33m"       # gold/yellow
    RED = "\033[31m"        # red
    GREEN = "\033[32m"      # green
    CYAN = "\033[36m"       # cyan
    WHITE = "\033[97m"      # bright white
    DIM = "\033[2m"         # dim
    BOLD = "\033[1m"        # bold
    RESET = "\033[0m"       # reset

    def __init__(self, typewriter: bool = True):
        self.typewriter = typewriter

    def _type(self, text: str, speed: float = 0.015):
        """Typewriter effect for narrative text."""
        if not self.typewriter:
            print(text)
            return
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            if char in ".!?":
                time.sleep(speed * 3)
            elif char == ",":
                time.sleep(speed * 2)
            elif char == "\n":
                time.sleep(speed)
            else:
                time.sleep(speed)
        print()

    def show_title_screen(self):
        print(f"\n{self.BOLD}{self.WHITE}")
        print("=" * 60)
        print("        THE LAST SUPPER AT ROSETTI'S")
        print("        A Murder Mystery SQL Game")
        print("=" * 60)
        print(f"{self.RESET}")

    def show_schema(self, schema_text: str):
        print(f"{self.CYAN}{schema_text}{self.RESET}")

    def show_intro(self, text: str):
        print(f"{self.NOIR}")
        self._type(text)
        print(f"{self.RESET}")

    def show_turn_header(self, state: GameState):
        phase_labels = {
            "scene_setting": "SCENE SETTING",
            "investigation": "INVESTIGATION",
            "closing_in": "CLOSING IN",
            "resolution": "RESOLUTION",
        }
        phase = phase_labels.get(state.current_phase, state.current_phase.upper())
        print(f"\n{self.DIM}{'─' * 60}{self.RESET}")
        print(
            f"{self.BOLD}Turn {state.turn_number}/{state.max_turns}{self.RESET}"
            f"  {self.DIM}│{self.RESET}  {phase}"
            f"  {self.DIM}│{self.RESET}  Clues: {len(state.clues_found)}/8"
        )
        print(f"{self.DIM}{'─' * 60}{self.RESET}")

    def show_narrative(self, text: str):
        print(f"\n{self.NOIR}")
        self._type(text)
        print(f"{self.RESET}")

    def show_clue_discovery(self, clue_descriptions: List[str]):
        for desc in clue_descriptions:
            print(f"\n{self.GOLD}{self.BOLD}  [CLUE DISCOVERED]{self.RESET} {self.GOLD}{desc}{self.RESET}")

    def show_results_table(self, results: List[Dict[str, Any]], columns: List[str], max_rows: int = 10):
        """Display query results as a formatted table."""
        if not results:
            print(f"\n{self.DIM}  (no results){self.RESET}")
            return

        display_results = results[:max_rows]

        # Calculate column widths
        widths = {col: len(col) for col in columns}
        for row in display_results:
            for col in columns:
                val = str(row.get(col, ""))
                if len(val) > 40:
                    val = val[:37] + "..."
                widths[col] = max(widths[col], len(val))

        # Header
        header = " | ".join(col.ljust(widths[col]) for col in columns)
        separator = "-+-".join("-" * widths[col] for col in columns)
        print(f"\n{self.WHITE}  {header}{self.RESET}")
        print(f"  {self.DIM}{separator}{self.RESET}")

        # Rows
        for row in display_results:
            row_str = " | ".join(
                str(row.get(col, ""))[:40].ljust(widths[col])
                for col in columns
            )
            print(f"  {row_str}")

        if len(results) > max_rows:
            print(f"  {self.DIM}... and {len(results) - max_rows} more rows{self.RESET}")

    def show_clue_progress(self, state: GameState):
        found = len(state.clues_found)
        total = 8
        filled = "█" * found
        empty = "░" * (total - found)
        print(f"\n  {self.DIM}Clues: [{filled}{empty}] {found}/{total}{self.RESET}")

    def show_error(self, message: str):
        print(f"\n{self.RED}  {message}{self.RESET}")

    def show_hint(self, hint: str):
        print(f"\n{self.CYAN}  [HINT] {hint}{self.RESET}")

    def show_resolution_prompt(self):
        print(f"\n{self.BOLD}{self.WHITE}")
        print("=" * 60)
        print("  FINAL QUESTION")
        print("  Detective, who killed Marco Rosetti?")
        print("  State your accusation (type a name):")
        print("=" * 60)
        print(f"{self.RESET}")

    def show_final_score(self, state: GameState):
        found = len(state.clues_found)

        if found >= 7 and state.hints_used == 0:
            rating = "Master Detective"
        elif found >= 5:
            rating = "Senior Detective"
        elif found >= 3:
            rating = "Junior Detective"
        else:
            rating = "Rookie"

        print(f"\n{self.BOLD}{self.WHITE}")
        print("=" * 60)
        print("  CASE REPORT")
        print("=" * 60)
        print(f"{self.RESET}")
        print(f"  Clues discovered:  {found}/8")
        print(f"  Score:             {int(state.total_score)} points")
        print(f"  Hints used:        {state.hints_used}")
        print(f"  Queries executed:  {len(state.query_history)}")
        if state.sql_concepts_used:
            print(f"  SQL concepts:      {', '.join(state.sql_concepts_used)}")
        print(f"\n  {self.BOLD}Rating: {rating}{self.RESET}")
        print()

    def show_stuck_suggestion(self):
        print(f"\n  {self.DIM}Stuck? Type 'hint' for a clue, or 'schema' to review the tables.{self.RESET}")

    def get_input(self) -> str:
        try:
            return input(f"\n{self.GREEN}SQL> {self.RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return "quit"
