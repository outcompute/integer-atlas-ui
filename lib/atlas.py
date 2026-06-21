"""Query the Integer Atlas dataset that the CLI populated.

Primary path: open the CLI's atlas.duckdb read-only — this reuses the `numbers`
view the CLI built (same-column-group shards unioned across ranges, different
groups FULL-joined on n). For that view's absolute parquet paths to resolve, the
workspace must be mounted at the SAME path inside this container (see the UI README).

Fallback: if atlas.duckdb is absent or its view paths don't resolve here, build a
view directly over the parquet shards (union by name — adequate for a single
column group; cross-group joins are only correct via the primary path).
"""
import os

import duckdb


def workspace() -> str:
    return os.environ.get("INTEGER_ATLAS_HOME", os.path.expanduser("~/.integer-atlas"))


def connect() -> "duckdb.DuckDBPyConnection":
    ws = workspace()
    db = os.path.join(ws, "atlas.duckdb")
    if os.path.exists(db):
        try:
            con = duckdb.connect(db, read_only=True)
            con.execute("SELECT 1 FROM numbers LIMIT 1")  # probe that the view resolves
            return con
        except Exception:
            pass  # fall through to the parquet fallback

    con = duckdb.connect()  # in-memory
    shards = os.path.join(ws, "cache", "shards")
    pattern = os.path.join(shards, "*.parquet")
    con.execute(
        f"CREATE VIEW numbers AS "
        f"SELECT * FROM read_parquet('{pattern}', union_by_name => true)"
    )
    return con
