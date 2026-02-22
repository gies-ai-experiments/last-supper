"""
Game Engine - orchestrates the 10-turn murder mystery game loop.
"""

from lib.database import SQLiteAdapter
from agents.evaluator import SQLEvaluator
from agents.storyteller import StorytellerAgent
from game.state import GameState
from game.display import Display
from mystery.schema import DDL_STATEMENTS, SEED_STATEMENTS
from mystery.story import MYSTERY_TITLE, SCHEMA_DESCRIPTION, INTRO_TEXT
from mystery.clues import get_all_clues


class GameEngine:
    def __init__(self, api_key: str = None, typewriter: bool = True):
        # Set up database
        self.adapter = SQLiteAdapter(":memory:")
        self.adapter.connect()
        self._setup_database()

        # Initialize components
        self.evaluator = SQLEvaluator(self.adapter)
        self.storyteller = StorytellerAgent(api_key=api_key)
        self.state = GameState()
        self.display = Display(typewriter=typewriter)
        self.clues = get_all_clues()

        # Track consecutive turns without clues for hint suggestion
        self._turns_without_clues = 0

    def _setup_database(self):
        """Create tables and seed data."""
        for ddl in DDL_STATEMENTS:
            result = self.adapter.execute(ddl)
            if not result.success:
                raise RuntimeError(f"Failed to create table: {result.error}")

        for insert in SEED_STATEMENTS:
            result = self.adapter.execute(insert)
            if not result.success:
                raise RuntimeError(f"Failed to seed data: {result.error}")

    def run(self):
        """Main game loop."""
        self.display.show_title_screen()
        self.display.show_schema(SCHEMA_DESCRIPTION)

        # Opening narration
        try:
            intro = self.storyteller.narrate_intro()
            self.display.show_narrative(intro)
        except Exception:
            self.display.show_intro(INTRO_TEXT)

        while not self.state.game_over:
            self.state.turn_number += 1

            if self.state.current_phase == "resolution":
                self._handle_resolution()
                break

            self._handle_turn()

        self.display.show_final_score(self.state)

    def _handle_turn(self):
        """Handle a single turn of the game."""
        self.display.show_turn_header(self.state)

        # Suggest hints if stuck
        if self._turns_without_clues >= 2:
            self.display.show_stuck_suggestion()

        while True:
            user_input = self.display.get_input()

            if not user_input:
                continue

            if user_input.lower() == "quit":
                self.state.game_over = True
                return

            if user_input.lower() == "schema":
                self.display.show_schema(SCHEMA_DESCRIPTION)
                continue

            if user_input.lower() == "hint":
                self._handle_hint()
                continue

            # Evaluate the SQL query
            eval_result = self.evaluator.evaluate(user_input)

            if not eval_result.is_valid:
                self.display.show_error(eval_result.feedback)
                continue  # Don't consume turn

            if not eval_result.executed:
                self.display.show_error(eval_result.feedback)
                continue  # Don't consume turn

            # Show results table
            self.display.show_results_table(
                eval_result.results,
                eval_result.columns,
            )

            # Record new clues
            new_clue_descriptions = []
            for clue_id in eval_result.new_clues_found:
                if clue_id not in self.state.clues_found:
                    self.state.clues_found.append(clue_id)
                    clue = self.clues[clue_id]
                    self.state.total_score += clue.points
                    new_clue_descriptions.append(clue.description)

            # Track concepts
            self.state.record_query(
                user_input, eval_result.new_clues_found, eval_result.sql_concepts
            )

            # Show clue discoveries
            if new_clue_descriptions:
                self.display.show_clue_discovery(new_clue_descriptions)
                self._turns_without_clues = 0
            else:
                self._turns_without_clues += 1

            # Narrate discovery
            try:
                narrative = self.storyteller.narrate_discovery(
                    sql_query=user_input,
                    query_results=eval_result.results,
                    clues_found=self.state.clues_found,
                    new_clues=eval_result.new_clues_found,
                    turn_number=self.state.turn_number,
                    total_turns=self.state.max_turns,
                )
                self.display.show_narrative(narrative)
            except Exception as e:
                # Fallback if LLM API fails
                if eval_result.new_clues_found:
                    self.display.show_narrative(
                        "The detective finds something interesting in the data..."
                    )
                else:
                    self.display.show_narrative(
                        "The detective studies the results, looking for connections..."
                    )

            self.display.show_clue_progress(self.state)
            break  # Turn consumed

    def _handle_hint(self):
        """Provide a hint to the player."""
        self.state.hints_used += 1

        hint = self.evaluator.get_hint(self.state.clues_found)
        if hint:
            # Try to get a narrative hint from the storyteller
            try:
                narrative_hint = self.storyteller.get_hint(
                    [hint], self.state.turn_number
                )
                self.display.show_hint(narrative_hint)
            except Exception:
                self.display.show_hint(hint)
        else:
            self.display.show_hint(
                "You've found all the clues! Make your accusation on the final turn."
            )

    def _handle_resolution(self):
        """Handle the final resolution turn."""
        self.display.show_turn_header(self.state)
        self.display.show_resolution_prompt()

        accusation = self.display.get_input()

        if accusation.lower() == "quit":
            self.state.game_over = True
            return

        is_correct = "sofia" in accusation.lower() or "chen" in accusation.lower()

        self.state.accusation = accusation
        self.state.game_over = True

        # Bonus points for correct accusation
        if is_correct:
            self.state.total_score += 30

        resolution = self.storyteller.deliver_resolution(
            accusation, is_correct, self.state.clues_found
        )
        self.display.show_narrative(resolution)

    def cleanup(self):
        """Clean up resources."""
        self.adapter.close()
