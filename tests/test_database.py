import sqlite3

import pandas as pd
import pytest

from src.database import (
    create_indexes,
    create_jasc_tables,
    create_reports_table,
    load_jasc_categories,
    load_jasc_codes,
    load_reports,
)


def make_test_data():
    # small dataset for testing database behaviour
    return pd.DataFrame(
        [
            {
                "operator_control_number": "TEST001",
                "difficulty_date": "2025-01-15",
                "submission_date": "2025-01-16T15:30:00+00:00",
                "jasc_code": "5320",
                "registry_number": "N123AB",
                "aircraft_make": "BOEING",
                "aircraft_model": "7378H4",
                "aircraft_serial_number": "ABC123",
                "aircraft_total_time": 12000.0,
                "aircraft_total_cycles": 8000.0,
                "part_make": "BOEING",
                "part_name": "HINGE",
                "part_number": "P123",
                "part_condition": "DAMAGED",
                "part_location": "LEFT WING",
                "stage_of_operation_code": "IN",
                "how_discovered_code": "O",
                "discrepancy": "Found crack in left wing.",
            },
            {
                "operator_control_number": "TEST002",
                "difficulty_date": "2025-02-20",
                "submission_date": "2025-02-21T19:00:00+00:00",
                "jasc_code": "3350",
                "registry_number": "N456CD",
                "aircraft_make": None,
                "aircraft_model": None,
                "aircraft_serial_number": "DEF456",
                "aircraft_total_time": 5000.0,
                "aircraft_total_cycles": 3000.0,
                "part_make": None,
                "part_name": "SENSOR",
                "part_number": None,
                "part_condition": "FAILED",
                "part_location": "LANDING GEAR",
                "stage_of_operation_code": "IN",
                "how_discovered_code": "O",
                "discrepancy": "Landing gear unsafe indication.",
            },
        ]
    )


def make_jasc_categories():
    return pd.DataFrame(
        [
            {
                "category_code": "53",
                "category_name": "FUSELAGE",
            },
        ]
    )


def make_jasc_codes():
    return pd.DataFrame(
        [
            {
                "jasc_code": "5320",
                "code_name": "FUSELAGE MISCELLANEOUS STRUCTURE",
                "code_desc": "Fuselage miscellaneous structure reports.",
            },
        ]
    )


def make_database():
    # use an in-memory database so tests do not touch the real database
    connection = sqlite3.connect(":memory:")
    create_reports_table(connection)

    return connection


def test_reports_can_be_inserted():
    connection = make_database()

    load_reports(connection, make_test_data())

    count = connection.execute(
        "SELECT COUNT(*) FROM maintenance_reports"
    ).fetchone()[0]

    connection.close()

    assert count == 2


def test_primary_key_prevents_duplicate_reports():
    connection = make_database()
    test_data = make_test_data()

    load_reports(connection, test_data)

    with pytest.raises(sqlite3.IntegrityError):
        load_reports(connection, test_data.iloc[[0]])

    connection.close()


def test_missing_aircraft_information_is_allowed():
    connection = make_database()

    load_reports(connection, make_test_data())

    result = connection.execute(
        """
        SELECT aircraft_make, aircraft_model
        FROM maintenance_reports
        WHERE operator_control_number = ?
        """,
        ("TEST002",),
    ).fetchone()

    connection.close()

    assert result == (None, None)


def test_required_fields_cannot_be_missing():
    connection = make_database()
    test_data = make_test_data()

    test_data.loc[0, "jasc_code"] = None

    with pytest.raises(sqlite3.IntegrityError):
        load_reports(connection, test_data)

    connection.close()


def test_indexes_are_created():
    connection = make_database()

    create_indexes(connection)

    indexes = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'index'
        AND name LIKE 'idx_%'
        """
    ).fetchall()

    connection.close()

    index_names = {index[0] for index in indexes}

    assert "idx_reports_aircraft" in index_names
    assert "idx_reports_date" in index_names
    assert "idx_reports_jasc" in index_names
    assert "idx_reports_part" in index_names


def test_jasc_reference_tables_are_created():
    connection = make_database()

    create_jasc_tables(connection)

    tables = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name IN (
              'jasc_codes',
              'jasc_categories'
          )
        """
    ).fetchall()

    connection.close()

    table_names = {table[0] for table in tables}

    assert table_names == {
        "jasc_codes",
        "jasc_categories",
    }


def test_jasc_reference_records_are_loaded():
    connection = make_database()

    create_jasc_tables(connection)
    load_jasc_categories(connection, make_jasc_categories())
    load_jasc_codes(connection, make_jasc_codes())

    code = connection.execute(
        """
        SELECT code_name, code_desc
        FROM jasc_codes
        WHERE jasc_code = ?
        """,
        ("5320",),
    ).fetchone()

    category = connection.execute(
        """
        SELECT category_name
        FROM jasc_categories
        WHERE category_code = ?
        """,
        ("53",),
    ).fetchone()

    connection.close()

    assert code == (
        "FUSELAGE MISCELLANEOUS STRUCTURE",
        "Fuselage miscellaneous structure reports.",
    )
    assert category == ("FUSELAGE",)
