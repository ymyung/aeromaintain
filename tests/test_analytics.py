import sqlite3

import pandas as pd

from src.analytics import (
    get_aircraft_summary,
    get_jasc_codes_for_aircraft,
    get_models_for_make,
    get_reports_by_month,
    get_reports_by_month_for_aircraft,
    get_reports_for_aircraft,
    get_top_aircraft_makes,
    get_top_parts,
    get_top_parts_for_aircraft,
    get_total_reports,
    search_aircraft_reports,
)
from src.database import (
    create_jasc_tables,
    create_reports_table,
    load_jasc_categories,
    load_jasc_codes,
    load_reports,
)


def make_test_data():
    # small known dataset so the expected query results are easy to check
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


def make_jasc_categories():
    return pd.DataFrame(
        [
            {
                "category_code": "33",
                "category_name": "LIGHTS",
            },
            {
                "category_code": "52",
                "category_name": "DOORS",
            },
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
                "jasc_code": "3350",
                "code_name": "EMERGENCY LIGHTING",
                "code_desc": "Emergency lighting system reports.",
            },
            {
                "jasc_code": "5210",
                "code_name": "PASSENGER/CREW DOORS",
                "code_desc": "Passenger and crew door reports.",
            },
            {
                "jasc_code": "5320",
                "code_name": "FUSELAGE MISCELLANEOUS STRUCTURE",
                "code_desc": "Fuselage miscellaneous structure reports.",
            },
        ]
    )


def make_database():
    # in-memory databases disappear when the connection is closed
    connection = sqlite3.connect(":memory:")

    create_reports_table(connection)
    load_reports(connection, make_test_data())

    create_jasc_tables(connection)
    load_jasc_categories(connection, make_jasc_categories())
    load_jasc_codes(connection, make_jasc_codes())

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
    assert result.iloc[1]["aircraft_make"] == "AIRBUS"
    assert result.iloc[1]["report_count"] == 1


def test_top_aircraft_makes_excludes_missing_values():
    connection = make_database()

    result = get_top_aircraft_makes(connection)

    connection.close()

    assert result["aircraft_make"].isna().sum() == 0


def test_top_aircraft_makes_limit():
    connection = make_database()

    result = get_top_aircraft_makes(
        connection,
        limit=1,
    )

    connection.close()

    assert len(result) == 1
    assert result.iloc[0]["aircraft_make"] == "BOEING"


def test_models_for_make():
    connection = make_database()

    result = get_models_for_make(
        connection,
        "BOEING",
    )

    connection.close()

    assert len(result) == 2
    assert result.iloc[0]["aircraft_model"] == "7378H4"
    assert result.iloc[0]["report_count"] == 2
    assert result.iloc[1]["aircraft_model"] == "737823"
    assert result.iloc[1]["report_count"] == 1


def test_models_for_make_only_returns_selected_make():
    connection = make_database()

    result = get_models_for_make(
        connection,
        "AIRBUS",
    )

    connection.close()

    assert len(result) == 1
    assert result.iloc[0]["aircraft_model"] == "A320232"
    assert result.iloc[0]["report_count"] == 1


def test_top_parts():
    connection = make_database()

    result = get_top_parts(connection)

    connection.close()

    assert result.iloc[0]["report_count"] == 2
    assert result.iloc[1]["report_count"] == 2

    returned_parts = set(result["part_name"])

    assert "HINGE" in returned_parts
    assert "VALVE" in returned_parts


def test_top_parts_limit():
    connection = make_database()

    result = get_top_parts(
        connection,
        limit=1,
    )

    connection.close()

    assert len(result) == 1


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


def test_top_parts_for_wrong_aircraft_is_empty():
    connection = make_database()

    result = get_top_parts_for_aircraft(
        connection,
        "BOEING",
        "DOES_NOT_EXIST",
    )

    connection.close()

    assert result.empty


def test_reports_by_month():
    connection = make_database()

    result = get_reports_by_month(connection)

    connection.close()

    assert len(result) == 3

    january = result[result["month"] == "2025-01"].iloc[0]
    february = result[result["month"] == "2025-02"].iloc[0]
    march = result[result["month"] == "2025-03"].iloc[0]

    assert january["report_count"] == 2
    assert february["report_count"] == 2
    assert march["report_count"] == 1
    assert result["month"].tolist() == [
        "2025-01",
        "2025-02",
        "2025-03",
    ]


def test_aircraft_summary():
    connection = make_database()

    result = get_aircraft_summary(
        connection,
        "BOEING",
        "7378H4",
    )

    connection.close()

    summary = result.iloc[0]

    assert summary["report_count"] == 2
    assert summary["unique_parts"] == 1
    assert summary["unique_jasc_codes"] == 1
    assert summary["first_report_date"] == "2025-01-10"
    assert summary["latest_report_date"] == "2025-01-20"


def test_reports_by_month_for_aircraft():
    connection = make_database()

    result = get_reports_by_month_for_aircraft(
        connection,
        "BOEING",
        "7378H4",
    )

    connection.close()

    assert len(result) == 1
    assert result.iloc[0]["month"] == "2025-01"
    assert result.iloc[0]["report_count"] == 2


def test_reports_for_aircraft_are_enriched_and_newest_first():
    connection = make_database()

    result = get_reports_for_aircraft(
        connection,
        "BOEING",
        "7378H4",
    )

    connection.close()

    assert len(result) == 2
    assert result["difficulty_date"].tolist() == [
        "2025-01-20",
        "2025-01-10",
    ]
    assert (
        result.iloc[0]["jasc_name"]
        == "FUSELAGE MISCELLANEOUS STRUCTURE"
    )
    assert result.iloc[0]["jasc_category"] == "FUSELAGE"


def test_reports_for_aircraft_limit():
    connection = make_database()

    result = get_reports_for_aircraft(
        connection,
        "BOEING",
        "7378H4",
        limit=1,
    )

    connection.close()

    assert len(result) == 1


def test_jasc_codes_for_aircraft():
    connection = make_database()

    result = get_jasc_codes_for_aircraft(
        connection,
        "BOEING",
        "7378H4",
    )

    connection.close()

    assert len(result) == 1
    assert result.iloc[0]["jasc_code"] == "5320"
    assert (
        result.iloc[0]["code_name"]
        == "FUSELAGE MISCELLANEOUS STRUCTURE"
    )
    assert result.iloc[0]["category_name"] == "FUSELAGE"
    assert result.iloc[0]["report_count"] == 2


def test_search_aircraft_reports_without_filters():
    connection = make_database()

    result = search_aircraft_reports(
        connection,
        "BOEING",
        "7378H4",
    )

    connection.close()

    assert len(result) == 2
    assert (
        result.iloc[0]["jasc_name"]
        == "FUSELAGE MISCELLANEOUS STRUCTURE"
    )
    assert result.iloc[0]["jasc_category"] == "FUSELAGE"


def test_search_aircraft_reports_by_text():
    connection = make_database()

    result = search_aircraft_reports(
        connection,
        "BOEING",
        "7378H4",
        search_text="damaged",
    )

    connection.close()

    assert len(result) == 1
    assert "damaged" in result.iloc[0]["discrepancy"].lower()
    assert (
        result.iloc[0]["jasc_name"]
        == "FUSELAGE MISCELLANEOUS STRUCTURE"
    )
    assert result.iloc[0]["jasc_category"] == "FUSELAGE"


def test_search_aircraft_reports_text_is_case_insensitive():
    connection = make_database()

    result = search_aircraft_reports(
        connection,
        "BOEING",
        "7378H4",
        search_text="DAMAGED",
    )

    connection.close()

    assert len(result) == 1
    assert "damaged" in result.iloc[0]["discrepancy"].lower()


def test_search_aircraft_reports_by_jasc():
    connection = make_database()

    result = search_aircraft_reports(
        connection,
        "BOEING",
        "7378H4",
        jasc_code="5320",
    )

    connection.close()

    assert len(result) == 2
    assert (result["jasc_code"] == "5320").all()
    assert (
        result["jasc_name"]
        == "FUSELAGE MISCELLANEOUS STRUCTURE"
    ).all()
    assert (result["jasc_category"] == "FUSELAGE").all()


def test_search_aircraft_reports_with_both_filters():
    connection = make_database()

    result = search_aircraft_reports(
        connection,
        "BOEING",
        "7378H4",
        search_text="wear",
        jasc_code="5320",
    )

    connection.close()

    assert len(result) == 1
    assert result.iloc[0]["jasc_code"] == "5320"
    assert "wear" in result.iloc[0]["discrepancy"].lower()
    assert (
        result.iloc[0]["jasc_name"]
        == "FUSELAGE MISCELLANEOUS STRUCTURE"
    )
    assert result.iloc[0]["jasc_category"] == "FUSELAGE"


def test_search_aircraft_reports_with_no_matches():
    connection = make_database()

    result = search_aircraft_reports(
        connection,
        "BOEING",
        "7378H4",
        search_text="this should not exist",
    )

    connection.close()

    assert result.empty


def test_search_aircraft_reports_wrong_jasc_returns_no_matches():
    connection = make_database()

    result = search_aircraft_reports(
        connection,
        "BOEING",
        "7378H4",
        jasc_code="9999",
    )

    connection.close()

    assert result.empty


def test_search_aircraft_reports_limit():
    connection = make_database()

    result = search_aircraft_reports(
        connection,
        "BOEING",
        "7378H4",
        limit=1,
    )

    connection.close()

    assert len(result) == 1


def test_search_aircraft_reports_returns_newest_first():
    connection = make_database()

    result = search_aircraft_reports(
        connection,
        "BOEING",
        "7378H4",
    )

    connection.close()

    assert result.iloc[0]["difficulty_date"] == "2025-01-20"
    assert result.iloc[1]["difficulty_date"] == "2025-01-10"
