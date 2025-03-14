import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

import rich
from tibiatools.queries import get_damage_dealers
from tibiatools.server_log_parser import parse_server_log


@pytest.fixture
def sample_df():
    """Create a sample DataFrame with combat data."""
    return pd.DataFrame(
        {
            "actor": ["Player1", "Player1", "Player2", "Player3"],
            "target": ["Boss1", "Boss1", "Boss1", "Boss2"],
            "action": ["damage", "damage", "damage", "damage"],
            "points": [100, 150, 200, 300],
        }
    )


@patch("duckdb.sql")
def test_get_damage_dealers_query(mock_sql, sample_df):
    """Test if the function calls SQL with the correct query."""
    # Setup mock
    mock_result = MagicMock()
    mock_sql.return_value = mock_result

    # Call function
    result = get_damage_dealers("test_df")

    # Check if SQL was called with correct query
    expected_query = """
        SELECT actor, target, SUM(points) as damage_count
        FROM test_df
        WHERE action = 'damage'
        GROUP BY actor, target
        ORDER BY actor, damage_count DESC
    """

    mock_sql.assert_called_once()
    actual_query = mock_sql.call_args[0][0].strip()
    expected_query = expected_query.strip()
    assert actual_query == expected_query
    assert result == mock_result


@patch("duckdb.sql")
def test_get_damage_dealers_result(mock_sql):
    """Test if the function returns the expected result."""
    # Setup mock result
    expected_df = pd.DataFrame(
        {
            "actor": ["Player1", "Player2", "Player3"],
            "target": ["Boss1", "Boss1", "Boss2"],
            "damage_count": [250, 200, 300],
        }
    )
    mock_sql.return_value = expected_df

    # Call function and assert result
    result = get_damage_dealers("combat_data")
    pd.testing.assert_frame_equal(result, expected_df)


@patch("duckdb.sql")
def test_get_damage_dealers_empty(mock_sql):
    """Test behavior with empty result."""
    # Setup mock with empty DataFrame
    mock_sql.return_value = pd.DataFrame(columns=["actor", "target", "damage_count"])

    # Call function
    result = get_damage_dealers("empty_df")

    # Assert result is empty DataFrame with expected columns
    assert result.empty
    assert list(result.columns) == ["actor", "target", "damage_count"]


@patch("duckdb.sql")
def test_get_damage_dealers_with_non_damage_actions(mock_sql):
    """Test with mixed action types to ensure only damage is counted."""
    # Call function
    get_damage_dealers("mixed_actions_df")

    # Check SQL query filters for damage actions only
    query = mock_sql.call_args[0][0]
    assert "WHERE action = 'damage'" in query


def test_aa():
    df = parse_server_log(
        r"C:\Users\janwa\AppData\Local\Tibia\packages\Tibia\log\Server Log.txt"
    )
    a = get_damage_dealers(df)
    rich.print(a)
