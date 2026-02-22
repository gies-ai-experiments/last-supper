"""SQLite database adapter for query execution and schema introspection."""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import time

from .models import ColumnInfo, TableInfo, SchemaSnapshot


@dataclass
class ExecutionResult:
    """Result of SQL query execution."""
    success: bool
    data: List[Dict[str, Any]]
    columns: List[str]
    rows_returned: int
    execution_time_ms: float
    error: Optional[str] = None
    dialect: str = ""


class SQLiteAdapter:
    """
    SQLite database adapter.
    Uses Python's built-in sqlite3 module. Supports in-memory databases.
    """

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        import sqlite3
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None

    def get_dialect(self) -> str:
        return "sqlite"

    def get_schema_snapshot(self) -> SchemaSnapshot:
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()
        tables = {}

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)

        for (table_name,) in cursor.fetchall():
            cursor.execute(f"PRAGMA table_info('{table_name}')")
            columns = []

            for row in cursor.fetchall():
                columns.append(ColumnInfo(
                    name=row[1],
                    dtype=row[2] or "TEXT",
                    nullable=not bool(row[3]),
                    primary_key=bool(row[5]),
                    default=row[4],
                ))

            cursor.execute(f"PRAGMA foreign_key_list('{table_name}')")
            for fk_row in cursor.fetchall():
                from_col = fk_row[3]
                to_table = fk_row[2]
                to_col = fk_row[4]

                for col in columns:
                    if col.name == from_col:
                        col.foreign_key = f"{to_table}.{to_col}"
                        break

            try:
                cursor.execute(f"SELECT COUNT(*) FROM '{table_name}'")
                row_count = cursor.fetchone()[0]
            except Exception:
                row_count = None

            tables[table_name] = TableInfo(
                name=table_name,
                columns=columns,
                row_count=row_count,
            )

        return SchemaSnapshot(
            dialect="sqlite",
            database=self.db_path,
            tables=tables,
        )

    def execute(self, sql: str) -> ExecutionResult:
        if not self.conn:
            self.connect()

        start_time = time.time()

        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)

            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                data = [dict(zip(columns, row)) for row in rows]

                elapsed = (time.time() - start_time) * 1000
                return ExecutionResult(
                    success=True,
                    data=data,
                    columns=columns,
                    rows_returned=len(data),
                    execution_time_ms=elapsed,
                    dialect="sqlite",
                )
            else:
                self.conn.commit()
                elapsed = (time.time() - start_time) * 1000
                return ExecutionResult(
                    success=True,
                    data=[],
                    columns=[],
                    rows_returned=cursor.rowcount,
                    execution_time_ms=elapsed,
                    dialect="sqlite",
                )

        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            return ExecutionResult(
                success=False,
                data=[],
                columns=[],
                rows_returned=0,
                execution_time_ms=elapsed,
                error=str(e),
                dialect="sqlite",
            )

    def execute_many(self, statements: List[str]) -> List[ExecutionResult]:
        results = []
        for sql in statements:
            results.append(self.execute(sql))
        return results
