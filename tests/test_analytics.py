import sqlite3

import pandas as pd

from src.analytics import (
    get_models_for_make,
    get_reports_by_month,
    get_top_aircraft_makes,
    get_top_parts,
    get_top_parts_for_aircraft,
    get_total_reports,
)
from src.database import create_reports_table, load_reports


def make_test_data():
    # small dataset for testing analytics queries
    return pd.DataFrame(
        [
            {
                "operator_control_number": "TEST001",
                "difficulty_date": "2025-01-10",
                "submission_date": "2025-01-11T12:00:00+00:00",
                "jasc_code": "5320",
                "registry_number": "N001AA",
                "aircraft_make": "BOEING",
                "aircraft_model": "7378H4",
                "aircraft_serial_number": "ABC001",
                "aircraft_total_time": 10000.0,
                "aircraft_total_cycles": 6000.0,
                "part_make": "BOEING",
                "part_name": "HINGE",
                "part_number": "P001",
                "part_condition": "DAMAGED",
                "part_location": "WING",
                "stage_of_operation_code": "IN",
                "how_discovered_code": "O",
                "discrepancy": "Found damaged hinge.",
            },
            {
                "operator_control_number": "TEST002",
                "difficulty_date": "2025-01-20",
                "submission_date": "2025-01-21T12:00:00+00:00",
                "jasc_code": "5320",
                "registry_number": "N002AA",
                "aircraft_make": "BOEING",
                "aircraft_model": "7378H4",
                "aircraft_serial_number": "ABC002",
                "aircraft_total_time": 11000.0,
                "aircraft_total_cycles": 6500.0,
                "part_make": "BOEING",
                "part_name": "HINGE",
                "part_number": "P002",
                "part_condition": "WORN",
                "part_location": "WING",
                "stage_of_operation_code": "IN",
                "how_discovered_code": "O",
                "discrepancy": "Hinge showed excessive wear.",
            },
            {
                "operator_control_number": "TEST003",
                "difficulty_date": "2025-02-10",
                "submission_date": "2025-02-11T12:00:00+00:00",
                "jasc_code": "3350",
                "registry_number": "N003AA",
                "aircraft_make": "BOEING",
                "aircraft_model": "737823",
                "aircraft_serial_number": "ABC003",
                "aircraft_total_time": 9000.0,
                "aircraft_total_cycles": 5000.0,
                "part_make": "BOEING",
                "part_name": "SENSOR",
                "part_number": "P003",
                "part_condition": "FAILED",
                "part_location": "LANDING GEAR",
                "stage_of_operation_code": "IN",
                "how_discovered_code": "O",
                "discrepancy": "Landing gear sensor failed.",
            },
            {
                "operator_control_number": "TEST004",
                "difficulty_date": "2025-02-15",
                "submission_date": "2025-02-16T12:00:00+00:00",
                "jasc_code": "5210",
                "registry_number": "N004AA",
                "aircraft_make": "AIRBUS",
                "aircraft_model": "A320232",
                "aircraft_serial_number": "ABC004",
                "aircraft_total_time": 8000.0,
                "aircraft_total_cycles": 4500.0,
                "part_make": "AIRBUS",
                "part_name": "VALVE",
                "part_number": "P004",
                "part_condition": "FAILED",
                "part_location": "FUSELAGE",
                "stage_of_operation_code": "IN",
                "how_discovered_code": "O",
                "discrepancy": "Valve failure found during inspection.",
            },
            {
                "operator_control_number": "TEST005",
                "difficulty_date": "2025-03-05",
                "submission_date": "2025-03-06T12:00:00+00:00",
                "jasc_code": "5210",
                "registry_number": "N005AA",
                "aircraft_make": None,
                "aircraft_model": None,
                "aircraft_serial_number": "ABC005",
                "aircraft_total_time": 5000.0,
                "aircraft_total_cycles": 2500.0,
                "part_make": None,
                "part_name": "VALVE",
                "part_number": None,
                "part_condition": "FAILED",
                "part_location": "FUSELAGE",
                "stage_of_operation_code": "IN",
                "how_discovered_code": "O",
                "discrepancy": "Valve failed.",
            },
        ]
    )


def make_database():
    # use a temporary in-memory database
    connection = sqlite3.connect(":memory:")

    create_reports_table(connection)
    load_reports(connection, make_test_data())

    return connection


def test_total_reports():
    connection = make_database()

    result = get_total_reports(connection)

    connection.close()

    assert result == 5


def test_top_aircraft_makes():
    connection = make_database()

    result = get_top_aircraft_makes(connection)

    connection.close()

    assert result.iloc[0]["aircraft_make"] == "BOEING"
    assert result.iloc[0]["report_count"] == 3
    assert "AIRBUS" in result["aircraft_make"].values


def test_models_for_make():
    connection = make_database()

    result = get_models_for_make(connection, "BOEING")

    connection.close()

    assert result.iloc[0]["aircraft_model"] == "7378H4"
    assert result.iloc[0]["report_count"] == 2


def test_top_parts():
    connection = make_database()

    result = get_top_parts(connection)

    connection.close()

    assert result.iloc[0]["part_name"] in {"HINGE", "VALVE"}
    assert result.iloc[0]["report_count"] == 2


def test_top_parts_for_specific_aircraft():
    connection = make_database()

    result = get_top_parts_for_aircraft(
        connection,
        "BOEING",
        "7378H4",
    )

    connection.close()

    assert len(result) == 1
    assert result.iloc[0]["part_name"] == "HINGE"
    assert result.iloc[0]["report_count"] == 2


def test_reports_by_month():
    connection = make_database()

    result = get_reports_by_month(connection)

    connection.close()

    january = result[result["month"] == "2025-01"].iloc[0]
    february = result[result["month"] == "2025-02"].iloc[0]
    march = result[result["month"] == "2025-03"].iloc[0]

    assert january["report_count"] == 2
    assert february["report_count"] == 2
    assert march["report_count"] == 1