"""
Multi-dialect SQL parser using sqlglot.
"""

import sqlglot
from sqlglot import exp
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from .dialects import get_dialect_config


@dataclass
class IdentifierSet:
    """Extracted SQL identifiers from a query."""
    tables: List[str] = field(default_factory=list)
    columns: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    aliases: Dict[str, str] = field(default_factory=dict)
    select_aliases: Set[str] = field(default_factory=set)
    cte_columns: Dict[str, Set[str]] = field(default_factory=dict)

    def __post_init__(self):
        self.tables = list(dict.fromkeys(self.tables))
        self.columns = list(dict.fromkeys(self.columns))
        self.functions = list(dict.fromkeys(self.functions))


@dataclass
class ParsedSQL:
    """Result of parsing a SQL query."""
    ast: Any
    dialect: str
    identifiers: IdentifierSet
    raw_sql: str
    is_valid: bool = True
    parse_error: Optional[str] = None

    @property
    def query_type(self) -> str:
        if self.ast is None:
            return "UNKNOWN"
        return type(self.ast).__name__.upper()

    @property
    def is_select(self) -> bool:
        return isinstance(self.ast, exp.Select)


class MultiDialectSQLParser:
    def __init__(self, default_dialect: str = "sqlite"):
        self.default_dialect = default_dialect

    def parse(self, sql: str, dialect: str = None) -> ParsedSQL:
        dialect = dialect or self.default_dialect

        try:
            config = get_dialect_config(dialect)
            sqlglot_dialect = config.sqlglot_dialect
        except ValueError:
            sqlglot_dialect = dialect

        try:
            ast = sqlglot.parse_one(sql, read=sqlglot_dialect)
            identifiers = self._extract_identifiers(ast)

            return ParsedSQL(
                ast=ast,
                dialect=dialect,
                identifiers=identifiers,
                raw_sql=sql,
                is_valid=True,
            )

        except sqlglot.errors.ParseError as e:
            ast, fallback_dialect = self._parse_with_fallback(sql, dialect)

            if ast:
                identifiers = self._extract_identifiers(ast)
                return ParsedSQL(
                    ast=ast,
                    dialect=fallback_dialect or dialect,
                    identifiers=identifiers,
                    raw_sql=sql,
                    is_valid=True,
                )

            return ParsedSQL(
                ast=None,
                dialect=dialect,
                identifiers=IdentifierSet(),
                raw_sql=sql,
                is_valid=False,
                parse_error=str(e),
            )

        except Exception as e:
            return ParsedSQL(
                ast=None,
                dialect=dialect,
                identifiers=IdentifierSet(),
                raw_sql=sql,
                is_valid=False,
                parse_error=str(e),
            )

    def _parse_with_fallback(self, sql: str, primary_dialect: str) -> tuple:
        fallback_order = ["sqlite", "postgres", "duckdb", "bigquery", None]

        for fallback in fallback_order:
            if fallback == primary_dialect:
                continue
            try:
                ast = sqlglot.parse_one(sql, read=fallback)
                return (ast, fallback)
            except:
                continue

        try:
            ast = sqlglot.parse_one(
                sql,
                error_level=sqlglot.ErrorLevel.IGNORE
            )
            return (ast, primary_dialect)
        except:
            return (None, None)

    def _extract_identifiers(self, ast: Any) -> IdentifierSet:
        tables = []
        columns = []
        functions = []
        aliases = {}
        select_aliases: Set[str] = set()
        cte_columns: Dict[str, Set[str]] = {}

        if ast is None:
            return IdentifierSet()

        for cte in ast.find_all(exp.CTE):
            cte_name = None
            if hasattr(cte, 'alias') and cte.alias:
                cte_name = cte.alias
                aliases[cte.alias] = "(cte)"

            if cte_name:
                cte_cols = self._extract_cte_columns(cte)
                if cte_cols:
                    cte_columns[cte_name.lower()] = cte_cols

        for select in ast.find_all(exp.Select):
            sel_aliases = self._extract_select_aliases(select)
            select_aliases.update(sel_aliases)

        for table in ast.find_all(exp.Table):
            name = table.name
            if table.db:
                name = f"{table.db}.{name}"
            if table.catalog:
                name = f"{table.catalog}.{name}"
            if name:
                tables.append(name)
            if table.alias:
                aliases[table.alias] = table.name

        for col in ast.find_all(exp.Column):
            name = col.name
            if col.table:
                name = f"{col.table}.{name}"
            if name:
                columns.append(name)

        for func in ast.find_all(exp.Func):
            func_name = self._get_function_name(func)
            if func_name:
                functions.append(func_name)

        for subquery in ast.find_all(exp.Subquery):
            if subquery.alias:
                aliases[subquery.alias] = "(subquery)"
                subq_cols = self._extract_subquery_columns(subquery)
                if subq_cols:
                    cte_columns[subquery.alias.lower()] = subq_cols

        return IdentifierSet(
            tables=tables,
            columns=columns,
            functions=functions,
            aliases=aliases,
            select_aliases=select_aliases,
            cte_columns=cte_columns,
        )

    def _extract_select_aliases(self, select: exp.Select) -> Set[str]:
        aliases = set()
        if not select.expressions:
            return aliases
        for expr in select.expressions:
            if isinstance(expr, exp.Alias):
                alias_name = expr.alias
                if alias_name:
                    aliases.add(alias_name.lower())
            elif hasattr(expr, 'alias') and expr.alias:
                aliases.add(expr.alias.lower())
        return aliases

    def _extract_cte_columns(self, cte: exp.CTE) -> Set[str]:
        columns = set()
        cte_query = cte.this
        if cte_query is None:
            return columns

        select = None
        if isinstance(cte_query, exp.Select):
            select = cte_query
        else:
            selects = list(cte_query.find_all(exp.Select))
            if selects:
                select = selects[0]

        if select and select.expressions:
            for expr in select.expressions:
                col_name = self._get_expression_output_name(expr)
                if col_name:
                    columns.add(col_name.lower())

        return columns

    def _extract_subquery_columns(self, subquery: exp.Subquery) -> Set[str]:
        columns = set()
        inner = subquery.this
        if isinstance(inner, exp.Select) and inner.expressions:
            for expr in inner.expressions:
                col_name = self._get_expression_output_name(expr)
                if col_name:
                    columns.add(col_name.lower())
        return columns

    def _get_expression_output_name(self, expr: Any) -> Optional[str]:
        if isinstance(expr, exp.Alias):
            return expr.alias
        if hasattr(expr, 'alias') and expr.alias:
            return expr.alias
        if isinstance(expr, exp.Column):
            return expr.name
        if hasattr(expr, 'output_name'):
            return expr.output_name
        return None

    def _get_function_name(self, func: exp.Func) -> str:
        if hasattr(func, 'sql_name'):
            try:
                return func.sql_name().upper()
            except:
                pass

        class_name = type(func).__name__
        name_mapping = {
            "Anonymous": "ANONYMOUS",
            "Count": "COUNT", "Sum": "SUM", "Avg": "AVG",
            "Min": "MIN", "Max": "MAX",
            "Coalesce": "COALESCE", "If": "IF", "Case": "CASE",
            "Cast": "CAST", "Concat": "CONCAT",
            "Substring": "SUBSTRING", "Length": "LENGTH",
            "Upper": "UPPER", "Lower": "LOWER", "Trim": "TRIM",
            "Round": "ROUND", "Abs": "ABS", "Floor": "FLOOR", "Ceil": "CEIL",
            "DateDiff": "DATEDIFF", "DateAdd": "DATEADD",
            "CurrentDate": "CURRENT_DATE", "CurrentTimestamp": "CURRENT_TIMESTAMP",
        }

        return name_mapping.get(class_name, class_name.upper())

    def extract_tables(self, sql: str, dialect: str = None) -> List[str]:
        parsed = self.parse(sql, dialect)
        return parsed.identifiers.tables

    def extract_columns(self, sql: str, dialect: str = None) -> List[str]:
        parsed = self.parse(sql, dialect)
        return parsed.identifiers.columns

    def get_query_type(self, sql: str, dialect: str = None) -> str:
        parsed = self.parse(sql, dialect)
        return parsed.query_type
