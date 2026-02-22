"""
Clue definitions for the murder mystery.
Each clue maps SQL query results to narrative discoveries.
"""

from dataclasses import dataclass
from typing import Callable, List, Dict, Any


@dataclass
class Clue:
    clue_id: str
    description: str
    narrative_text: str
    difficulty: str  # "basic", "intermediate", "advanced"
    sql_concept: str
    hint_text: str
    points: int
    detection_function: Callable[[List[Dict[str, Any]]], bool]


def _detect_crime_scene(results: List[Dict[str, Any]]) -> bool:
    """Check if results reveal events at the private dining room near time of death."""
    for row in results:
        values = [str(v).lower() for v in row.values()]
        has_location = any(
            "private dining" in v or "dining_room" in v
            for v in values
        ) or row.get("location_id") == 2
        has_time = any("22:45" in v or "22:4" in v or "collapse" in v for v in values)
        if has_location and has_time:
            return True
    return False


def _detect_guest_list(results: List[Dict[str, Any]]) -> bool:
    """Check if results show who was at the restaurant that evening."""
    names_found = set()
    expected = {"marco", "elena", "vincent", "sofia", "james"}
    for row in results:
        for v in row.values():
            v_lower = str(v).lower()
            for name in expected:
                if name in v_lower:
                    names_found.add(name)
    return len(names_found) >= 3


def _detect_criminal_record(results: List[Dict[str, Any]]) -> bool:
    """Check if results reveal someone has a criminal record."""
    for row in results:
        has_record = row.get("has_criminal_record")
        if has_record == 1 or has_record is True:
            name = str(row.get("name", "")).lower()
            if "vincent" in name or "morrow" in name:
                return True
    return False


def _detect_last_call(results: List[Dict[str, Any]]) -> bool:
    """Check if results reveal Marco's last call was to Sofia."""
    for row in results:
        values = [str(v).lower() for v in row.values()]
        caller = row.get("caller_id")
        receiver = row.get("receiver_id")
        # Marco (1) called Sofia (4) at 22:15
        if caller == 1 and receiver == 4:
            return True
        # Or if they see the 22:15 call with person references
        if any("22:15" in v for v in values):
            if caller in (1, 4) or receiver in (1, 4):
                return True
    return False


def _detect_suspicious_purchase(results: List[Dict[str, Any]]) -> bool:
    """Check if results reveal Sofia's suspicious chemical purchase."""
    for row in results:
        values = [str(v).lower() for v in row.values()]
        has_amount = row.get("amount") == 487.5 or any("487" in v for v in values)
        has_chem = any("chemdirect" in v or "kitchen supplies" in v for v in values)
        has_sofia = row.get("person_id") == 4 or any("sofia" in v or "chen" in v for v in values)
        if (has_amount or has_chem) and has_sofia:
            return True
        if has_amount and has_chem:
            return True
    return False


def _detect_timeline_gap(results: List[Dict[str, Any]]) -> bool:
    """Check if results reveal Sofia's timeline gap (GROUP BY analysis)."""
    # This triggers when they group events by person and see counts/times
    person_ids_seen = set()
    for row in results:
        pid = row.get("person_id")
        if pid is not None:
            person_ids_seen.add(pid)

    # If they're looking at grouped data with multiple persons
    if len(person_ids_seen) >= 3:
        # Check if results include aggregate-like columns
        for row in results:
            col_names = [k.lower() for k in row.keys()]
            has_aggregate = any(
                c in col_names for c in
                ["count", "count(*)", "min_time", "max_time",
                 "min(event_time)", "max(event_time)", "cnt",
                 "num_events", "event_count"]
            )
            if has_aggregate:
                return True

    return False


def _detect_poison_evidence(results: List[Dict[str, Any]]) -> bool:
    """Check if results reveal physical evidence in the kitchen."""
    for row in results:
        values = [str(v).lower() for v in row.values()]
        has_kitchen = any("kitchen" in v for v in values) or row.get("location_id") == 3
        has_evidence = any(
            term in v
            for v in values
            for term in ["vial", "residue", "chemical", "cyanide"]
        )
        if has_kitchen and has_evidence:
            return True
        # Also detect if they find the wine evidence
        if any("cyanide" in v or "poison" in v for v in values):
            return True
    return False


def _detect_alibi_check(results: List[Dict[str, Any]]) -> bool:
    """Check if results reveal who was NOT at the dining room at time of death."""
    # This is triggered by subqueries or NOT IN patterns
    # Look for results that show a filtered set of persons
    names_found = set()
    for row in results:
        for v in row.values():
            v_lower = str(v).lower()
            if "elena" in v_lower:
                names_found.add("elena")
            if "sofia" in v_lower:
                names_found.add("sofia")
            if "daniela" in v_lower:
                names_found.add("daniela")

    # Elena left at 22:00, so she should show up in alibi checks
    # Sofia was unaccounted for during the gap
    if "elena" in names_found and len(names_found) <= 4:
        return True
    return False


def get_all_clues() -> Dict[str, Clue]:
    """Return all clue definitions."""
    return {
        "crime_scene": Clue(
            clue_id="crime_scene",
            description="Events at the private dining room near time of death",
            narrative_text=(
                "The detective's eyes narrow as the timeline crystallizes. "
                "The private dining room -- that's where it all went down. "
                "Marco collapsed at exactly 10:45 PM. Who was there? Who had access?"
            ),
            difficulty="basic",
            sql_concept="WHERE",
            hint_text="Try looking at events at a specific location around the time of death. The events table has location_id and event_time columns.",
            points=10,
            detection_function=_detect_crime_scene,
        ),
        "guest_list": Clue(
            clue_id="guest_list",
            description="Who was at the restaurant that evening",
            narrative_text=(
                "The detective pulls out a notepad. Five people, one victim. "
                "Each with their own reasons to be here tonight. "
                "The question isn't who was here -- it's who had something to hide."
            ),
            difficulty="basic",
            sql_concept="JOIN",
            hint_text="Join the persons table with the events table to see who was at the restaurant. Try using JOIN with ON to connect person_id.",
            points=10,
            detection_function=_detect_guest_list,
        ),
        "criminal_record": Clue(
            clue_id="criminal_record",
            description="Vincent Morrow has a criminal record",
            narrative_text=(
                "Well, well. Vincent Morrow -- Marco's business partner -- "
                "has a prior record. A wolf in an expensive suit. "
                "But a record doesn't make a killer. What was his angle?"
            ),
            difficulty="basic",
            sql_concept="WHERE",
            hint_text="Check the persons table for anyone with a criminal record. Look at the has_criminal_record column.",
            points=10,
            detection_function=_detect_criminal_record,
        ),
        "last_call": Clue(
            clue_id="last_call",
            description="Marco's last phone call was to Sofia Chen",
            narrative_text=(
                "The phone records don't lie. Marco's last call at 10:15 PM "
                "was to the head chef, Sofia Chen. Eight minutes. "
                "What do you say to your chef that takes eight minutes at that hour? "
                "And why did she look so shaken afterward?"
            ),
            difficulty="intermediate",
            sql_concept="JOIN + ORDER BY",
            hint_text="Look at the phone_records table. Try ordering by call_time to find the last calls. Who called whom?",
            points=15,
            detection_function=_detect_last_call,
        ),
        "suspicious_purchase": Clue(
            clue_id="suspicious_purchase",
            description="Sofia purchased chemicals from ChemDirect Inc.",
            narrative_text=(
                "Four hundred eighty-seven dollars and fifty cents. "
                "'Kitchen supplies' from a company called ChemDirect Inc. "
                "The detective has never seen a kitchen supply company "
                "with 'Chem' in the name. This changes everything."
            ),
            difficulty="intermediate",
            sql_concept="JOIN + WHERE",
            hint_text="Check the financial_records table for unusual transactions. Look for large amounts or suspicious descriptions. Try joining with persons to see who made each transaction.",
            points=20,
            detection_function=_detect_suspicious_purchase,
        ),
        "timeline_gap": Clue(
            clue_id="timeline_gap",
            description="Sofia has an unaccounted gap in her timeline",
            narrative_text=(
                "The numbers tell a story the witnesses missed. "
                "Everyone else has a continuous trail through the evening, "
                "but Sofia -- she vanishes from the record between 10:15 and 10:50. "
                "Thirty-five minutes unaccounted for. What was she doing?"
            ),
            difficulty="advanced",
            sql_concept="GROUP BY",
            hint_text="Try grouping events by person_id and counting them, or looking at MIN and MAX event times per person. Who has gaps in their timeline?",
            points=20,
            detection_function=_detect_timeline_gap,
        ),
        "poison_evidence": Clue(
            clue_id="poison_evidence",
            description="Physical evidence of poison found in the kitchen",
            narrative_text=(
                "There it is. A small glass vial with chemical residue, "
                "buried in the kitchen trash. And the wine -- "
                "the lab confirms traces of potassium cyanide. "
                "Someone turned a bottle of Barolo into a murder weapon."
            ),
            difficulty="intermediate",
            sql_concept="JOIN",
            hint_text="Look at the evidence table and join it with locations. What physical evidence was found, and where?",
            points=15,
            detection_function=_detect_poison_evidence,
        ),
        "alibi_check": Clue(
            clue_id="alibi_check",
            description="Cross-referencing who was NOT present at key moments",
            narrative_text=(
                "The detective leans back. Not everyone was in the dining room "
                "when Marco fell. Elena had already left. And Sofia? "
                "She wasn't where she said she was. The alibi doesn't hold."
            ),
            difficulty="advanced",
            sql_concept="Subquery / NOT IN",
            hint_text="Use a subquery with NOT IN to find persons who were NOT at a specific location after a certain time. Who was missing from the private dining room?",
            points=20,
            detection_function=_detect_alibi_check,
        ),
    }


TOTAL_CLUES = 8
TOTAL_POINTS = sum(c.points for c in get_all_clues().values())
