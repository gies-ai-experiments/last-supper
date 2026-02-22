"""
SQL Evaluator - validates, executes, and detects clues from player queries.
Wraps the vendored lib/ code. No LLM calls.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from lib.database import SQLiteAdapter, ExecutionResult
from lib.hallucination import HallucinationDetector, ValidationResult
from lib.sql_parser import MultiDialectSQLParser
from lib.models import SchemaSnapshot
from mystery.clues import get_all_clues, Clue


@dataclass
class EvaluationResult:
    is_valid: bool
    executed: bool
    results: List[Dict[str, Any]]
    columns: List[str]
    rows_returned: int
    execution_time_ms: float
    validation_errors: List[str]
    validation_warnings: List[str]
    new_clues_found: List[str]
    sql_concepts: List[str]
    feedback: str
    error: Optional[str] = None


class SQLEvaluator:
    def __init__(self, adapter: SQLiteAdapter):
        self.adapter = adapter
        self.schema = adapter.get_schema_snapshot()
        self.detector = HallucinationDetector(dialect="sqlite")
        self.parser = MultiDialectSQLParser(default_dialect="sqlite")
        self.clues = get_all_clues()
        self.found_clues: set = set()

    def evaluate(self, sql: str) -> EvaluationResult:
        """Full evaluation pipeline: validate -> execute -> detect clues."""
        sql = sql.strip().rstrip(";")
        if not sql:
            return EvaluationResult(
                is_valid=False, executed=False, results=[], columns=[],
                rows_returned=0, execution_time_ms=0,
                validation_errors=["Empty query"], validation_warnings=[],
                new_clues_found=[], sql_concepts=[], feedback="Please enter a SQL query.",
            )

        # Block non-SELECT statements
        first_word = sql.strip().split()[0].upper()
        if first_word not in ("SELECT", "WITH"):
            return EvaluationResult(
                is_valid=False, executed=False, results=[], columns=[],
                rows_returned=0, execution_time_ms=0,
                validation_errors=[f"Only SELECT queries are allowed (got {first_word})"],
                validation_warnings=[], new_clues_found=[], sql_concepts=[],
                feedback="Only SELECT queries are allowed, Detective. This is a read-only investigation.",
            )

        # Check for phantom tables only (column validation is too aggressive for learners)
        report = self.detector.detect(sql, self.schema)
        if report.phantom_tables:
            table_list = ", ".join(self.schema.table_names)
            errors = [f"Table '{t}' does not exist" for t in report.phantom_tables]
            return EvaluationResult(
                is_valid=False, executed=False, results=[], columns=[],
                rows_returned=0, execution_time_ms=0,
                validation_errors=errors, validation_warnings=[],
                new_clues_found=[], sql_concepts=[],
                feedback=f"Invalid table name(s): {', '.join(report.phantom_tables)}\n  Available tables: {table_list}",
            )

        # Execute the query directly — let SQLite handle syntax/column errors
        exec_result = self.adapter.execute(sql)

        if not exec_result.success:
            return EvaluationResult(
                is_valid=True, executed=False, results=[], columns=[],
                rows_returned=0, execution_time_ms=exec_result.execution_time_ms,
                validation_errors=[], validation_warnings=[],
                new_clues_found=[], sql_concepts=[],
                feedback=f"Query error: {exec_result.error}", error=exec_result.error,
            )

        # Detect clues from results
        new_clues = self._check_clues(exec_result.data)

        # Detect SQL concepts used
        concepts = self._detect_concepts(sql)

        # Build feedback
        if exec_result.rows_returned == 0:
            feedback = "Query executed successfully but returned no results."
        else:
            feedback = f"Query returned {exec_result.rows_returned} row(s)."
            if new_clues:
                feedback += " New clue(s) discovered!"

        return EvaluationResult(
            is_valid=True, executed=True,
            results=exec_result.data, columns=exec_result.columns,
            rows_returned=exec_result.rows_returned,
            execution_time_ms=exec_result.execution_time_ms,
            validation_errors=[], validation_warnings=[],
            new_clues_found=new_clues, sql_concepts=concepts,
            feedback=feedback,
        )

    def _check_clues(self, results: List[Dict[str, Any]]) -> List[str]:
        """Run detection functions against query results."""
        new_clues = []
        if not results:
            return new_clues

        for clue_id, clue in self.clues.items():
            if clue_id in self.found_clues:
                continue
            try:
                if clue.detection_function(results):
                    new_clues.append(clue_id)
                    self.found_clues.add(clue_id)
            except Exception:
                continue

        return new_clues

    def _detect_concepts(self, sql: str) -> List[str]:
        """Detect which SQL concepts the query uses."""
        sql_upper = sql.upper()
        concepts = []

        if "JOIN" in sql_upper:
            concepts.append("JOIN")
        if "WHERE" in sql_upper:
            concepts.append("WHERE")
        if "GROUP BY" in sql_upper:
            concepts.append("GROUP BY")
        if "ORDER BY" in sql_upper:
            concepts.append("ORDER BY")
        if "HAVING" in sql_upper:
            concepts.append("HAVING")
        if "NOT IN" in sql_upper or "NOT EXISTS" in sql_upper:
            concepts.append("Subquery")
        elif "SELECT" in sql_upper and sql_upper.count("SELECT") > 1:
            concepts.append("Subquery")
        if "WITH" in sql_upper:
            concepts.append("CTE")
        if any(f in sql_upper for f in ["ROW_NUMBER", "RANK", "LAG", "LEAD", "OVER("]):
            concepts.append("Window Function")
        if "COUNT" in sql_upper or "SUM" in sql_upper or "AVG" in sql_upper:
            concepts.append("Aggregate")
        if "LIKE" in sql_upper:
            concepts.append("LIKE")

        return concepts

    def _format_errors(self, validation: ValidationResult) -> str:
        """Format validation errors into friendly feedback."""
        parts = []
        for error in validation.errors:
            parts.append(f"  {error}")
        return "Invalid query:\n" + "\n".join(parts)

    def get_hint(self, found_clues: List[str]) -> Optional[str]:
        """Return a hint for the next undiscovered clue."""
        # Prioritize by difficulty: basic -> intermediate -> advanced
        priority = ["basic", "intermediate", "advanced"]

        for diff in priority:
            for clue_id, clue in self.clues.items():
                if clue_id not in found_clues and clue.difficulty == diff:
                    return clue.hint_text

        return None
