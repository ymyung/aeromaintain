import sqlite3
from pathlib import Path

import pandas as pd

# database location
database_file = Path("data/aeromaintain.db")


def get_total_reports(connection):
    # get the total number of maintenance reports
    result = connection.execute("SELECT COUNT(*) FROM maintenance_reports").fetchone()

    return result[0]


def get_top_aircraft_makes(connection, limit=10):
    # find manufacturers with the most reports
    query = """
        SELECT
            aircraft_make,
            COUNT(*) AS report_count
        FROM maintenance_reports
        WHERE aircraft_make IS NOT NULL
        GROUP BY aircraft_make
        ORDER BY report_count DESC
        LIMIT ?
    """

    return pd.read_sql_query(
        query,
        connection,
        params=(limit,),
    )


def get_models_for_make(connection, aircraft_make):
    # get aircraft models belonging to one manufacturer
    query = """
        SELECT
            aircraft_model,
            COUNT(*) AS report_count
        FROM maintenance_reports
        WHERE aircraft_make = ?
          AND aircraft_model IS NOT NULL
        GROUP BY aircraft_model
        ORDER BY report_count DESC, aircraft_model
    """

    return pd.read_sql_query(
        query,
        connection,
        params=(aircraft_make,),
    )


def get_top_parts(connection, limit=10):
    # find the most commonly reported parts
    query = """
        SELECT
            part_name,
            COUNT(*) AS report_count
        FROM maintenance_reports
        WHERE part_name IS NOT NULL
        GROUP BY part_name
        ORDER BY report_count DESC, part_name
        LIMIT ?
    """

    return pd.read_sql_query(
        query,
        connection,
        params=(limit,),
    )


def get_top_parts_for_aircraft(
    connection,
    aircraft_make,
    aircraft_model,
    limit=10,
):
    # find common reported parts for a specific aircraft
    query = """
        SELECT
            part_name,
            COUNT(*) AS report_count
        FROM maintenance_reports
        WHERE aircraft_make = ?
          AND aircraft_model = ?
          AND part_name IS NOT NULL
        GROUP BY part_name
        ORDER BY report_count DESC, part_name
        LIMIT ?
    """

    return pd.read_sql_query(
        query,
        connection,
        params=(
            aircraft_make,
            aircraft_model,
            limit,
        ),
    )


def get_reports_by_month(connection):
    # count how many reports occurred each month
    query = """
        SELECT
            substr(difficulty_date, 1, 7) AS month,
            COUNT(*) AS report_count
        FROM maintenance_reports
        GROUP BY month
        ORDER BY month
    """

    return pd.read_sql_query(
        query,
        connection,
    )


def get_reports_for_aircraft(
    connection,
    aircraft_make,
    aircraft_model,
    limit=100,
):
    # get individual reports for a selected aircraft
    query = """
        SELECT
            difficulty_date,
            jasc_code,
            part_name,
            part_condition,
            discrepancy
        FROM maintenance_reports
        WHERE aircraft_make = ?
          AND aircraft_model = ?
        ORDER BY difficulty_date DESC
        LIMIT ?
    """

    return pd.read_sql_query(
        query,
        connection,
        params=(
            aircraft_make,
            aircraft_model,
            limit,
        ),
    )


def get_aircraft_summary(
    connection,
    aircraft_make,
    aircraft_model,
):
    # basic summary numbers for one aircraft model
    query = """
        SELECT
            COUNT(*) AS report_count,
            COUNT(DISTINCT part_name) AS unique_parts,
            COUNT(DISTINCT jasc_code) AS unique_jasc_codes,
            MIN(difficulty_date) AS first_report_date,
            MAX(difficulty_date) AS latest_report_date
        FROM maintenance_reports
        WHERE aircraft_make = ?
          AND aircraft_model = ?
    """

    return pd.read_sql_query(
        query,
        connection,
        params=(
            aircraft_make,
            aircraft_model,
        ),
    )


def get_reports_by_month_for_aircraft(
    connection,
    aircraft_make,
    aircraft_model,
):
    # monthly report counts for one aircraft model
    query = """
        SELECT
            substr(difficulty_date, 1, 7) AS month,
            COUNT(*) AS report_count
        FROM maintenance_reports
        WHERE aircraft_make = ?
          AND aircraft_model = ?
        GROUP BY month
        ORDER BY month
    """

    return pd.read_sql_query(
        query,
        connection,
        params=(
            aircraft_make,
            aircraft_model,
        ),
    )


def search_aircraft_reports(
    connection,
    aircraft_make,
    aircraft_model,
    search_text="",
    jasc_code=None,
    limit=100,
):
    # build the query for reports from one aircraft model
    query = """
        SELECT
            difficulty_date,
            jasc_code,
            part_name,
            part_condition,
            discrepancy
        FROM maintenance_reports
        WHERE aircraft_make = ?
          AND aircraft_model = ?
    """

    params = [
        aircraft_make,
        aircraft_model,
    ]

    # optionally search the maintenance description
    if search_text:
        query += """
          AND discrepancy LIKE ?
        """

        params.append(f"%{search_text}%")

    # optionally filter by jasc code
    if jasc_code:
        query += """
          AND jasc_code = ?
        """

        params.append(jasc_code)

    query += """
        ORDER BY difficulty_date DESC
        LIMIT ?
    """

    params.append(limit)

    return pd.read_sql_query(
        query,
        connection,
        params=params,
    )


def get_jasc_codes_for_aircraft(
    connection,
    aircraft_make,
    aircraft_model,
):
    query = """
        SELECT
            jasc_code,
            COUNT(*) AS report_count
        FROM maintenance_reports
        WHERE aircraft_make = ?
          AND aircraft_model = ?
        GROUP BY jasc_code
        ORDER BY report_count DESC, jasc_code
    """

    return pd.read_sql_query(
        query,
        connection,
        params=(
            aircraft_make,
            aircraft_model,
        ),
    )


def main():
    with sqlite3.connect(database_file) as connection:
        print("\n=== TOTAL REPORTS ===")
        print(get_total_reports(connection))

        print("\n=== TOP AIRCRAFT MAKES ===")
        print(get_top_aircraft_makes(connection).to_string(index=False))

        print("\n=== BOEING MODELS ===")
        print(
            get_models_for_make(
                connection,
                "BOEING",
            )
            .head(10)
            .to_string(index=False)
        )

        print("\n=== TOP PARTS ===")
        print(get_top_parts(connection).to_string(index=False))

        print("\n=== REPORTS BY MONTH ===")
        print(get_reports_by_month(connection).to_string(index=False))


if __name__ == "__main__":
    main()
