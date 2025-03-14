import duckdb
import pandas as pd


def get_damage_dealers(df: pd.DataFrame) -> pd.DataFrame:
    """Select all damage dealers per boss."""
    duckdb.register("damage_data", df)

    return duckdb.sql(
        """
        SELECT actor, target, SUM(points) as damage_count
        FROM damage_data
        WHERE action = 'ATTACK' AND target != actor
        GROUP BY actor, target
        ORDER BY damage_count DESC
    """
    )
