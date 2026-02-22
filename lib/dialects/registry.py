"""
Dialect Registry - Configurations for supported SQL dialects.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Set, Dict


class Dialect(Enum):
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    BIGQUERY = "bigquery"
    SNOWFLAKE = "snowflake"
    DUCKDB = "duckdb"
    MYSQL = "mysql"


@dataclass
class DialectConfig:
    name: Dialect
    sqlglot_dialect: str
    default_schema: Optional[str]
    supports_schemas: bool
    supports_cte: bool = True
    supports_window_functions: bool = True
    supports_json: bool = False
    supports_arrays: bool = False
    builtin_functions: Set[str] = field(default_factory=set)
    description: str = ""


SQLITE_FUNCTIONS: Set[str] = {
    "AVG", "COUNT", "GROUP_CONCAT", "MAX", "MIN", "SUM", "TOTAL",
    "ABS", "CHANGES", "CHAR", "COALESCE", "GLOB", "HEX", "IFNULL",
    "IIF", "INSTR", "LAST_INSERT_ROWID", "LENGTH", "LIKE", "LIKELIHOOD",
    "LIKELY", "LOAD_EXTENSION", "LOWER", "LTRIM", "NULLIF",
    "PRINTF", "QUOTE", "RANDOM", "RANDOMBLOB", "REPLACE", "ROUND", "RTRIM",
    "SIGN", "SOUNDEX", "SUBSTR", "SUBSTRING",
    "TOTAL_CHANGES", "TRIM", "TYPEOF", "UNICODE", "UNLIKELY", "UPPER", "ZEROBLOB",
    "DATE", "TIME", "DATETIME", "JULIANDAY", "UNIXEPOCH", "STRFTIME",
    "TIMEDIFF", "CURRENT_DATE", "CURRENT_TIME", "CURRENT_TIMESTAMP",
    "ACOS", "ACOSH", "ASIN", "ASINH", "ATAN", "ATAN2", "ATANH",
    "CEIL", "CEILING", "COS", "COSH", "DEGREES", "EXP", "FLOOR",
    "LN", "LOG", "LOG10", "LOG2", "MOD", "PI", "POW", "POWER",
    "RADIANS", "SIN", "SINH", "SQRT", "TAN", "TANH", "TRUNC",
    "ROW_NUMBER", "RANK", "DENSE_RANK", "NTILE", "LAG", "LEAD",
    "FIRST_VALUE", "LAST_VALUE", "NTH_VALUE",
    "CUME_DIST", "PERCENT_RANK",
    "JSON", "JSON_ARRAY", "JSON_ARRAY_LENGTH", "JSON_EXTRACT",
    "JSON_INSERT", "JSON_OBJECT", "JSON_PATCH", "JSON_REMOVE",
    "JSON_REPLACE", "JSON_SET", "JSON_TYPE", "JSON_VALID",
    "JSON_QUOTE", "JSON_GROUP_ARRAY", "JSON_GROUP_OBJECT",
    "CAST", "TYPEOF",
}

DIALECT_CONFIGS: Dict[Dialect, DialectConfig] = {
    Dialect.SQLITE: DialectConfig(
        name=Dialect.SQLITE,
        sqlglot_dialect="sqlite",
        default_schema=None,
        supports_schemas=False,
        supports_cte=True,
        supports_window_functions=True,
        supports_json=True,
        supports_arrays=False,
        builtin_functions=SQLITE_FUNCTIONS,
        description="SQLite - Lightweight embedded database"
    ),
}


def get_dialect_config(dialect: str) -> DialectConfig:
    try:
        dialect_enum = Dialect(dialect.lower())
        return DIALECT_CONFIGS[dialect_enum]
    except (ValueError, KeyError):
        supported = ", ".join(d.value for d in Dialect if d in DIALECT_CONFIGS)
        raise ValueError(f"Unsupported dialect: {dialect}. Supported: {supported}")


def get_supported_dialects() -> list:
    return [d.value for d in Dialect if d in DIALECT_CONFIGS]
