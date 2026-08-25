import sqlite3
from pathlib import Path

import pandas as pd

database_file = Path(
    "data/aeromaintain.db"
)


def get_total_reports(connection):
    result = connection.execute(
        """
        SELECT COUNT(*)
        FROM maintenance_reports
        """
    ).fetchone()

    return result[0]


def get_top_aircraft_makes(
    connection,
    limit=10,
):
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


def get_models_for_make(
    connection,
    aircraft_make,
):
    query = """
        SELECT
            aircraft_model,
            COUNT(*) AS report_count
        FROM maintenance_reports
        WHERE aircraft_make = ?
          AND aircraft_model IS NOT NULL
        GROUP BY aircraft_model
        ORDER BY
            report_count DESC,
            aircraft_model
    """

    return pd.read_sql_query(
        query,
        connection,
        params=(aircraft_make,),
    )


def get_top_parts(
    connection,
    limit=10,
):
    query = """
        SELECT
            part_name,
            COUNT(*) AS report_count
        FROM maintenance_reports
        WHERE part_name IS NOT NULL
        GROUP BY part_name
        ORDER BY
            report_count DESC,
            part_name
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
    query = """
        SELECT
            part_name,
            COUNT(*) AS report_count
        FROM maintenance_reports
        WHERE aircraft_make = ?
          AND aircraft_model = ?
          AND part_name IS NOT NULL
        GROUP BY part_name
        ORDER BY
            report_count DESC,
            part_name
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
    query = """
        SELECT
            substr(
                difficulty_date,
                1,
                7
            ) AS month,
            COUNT(*) AS report_count
        FROM maintenance_reports
        GROUP BY month
        ORDER BY month
    """

    return pd.read_sql_query(
        query,
        connection,
    )


def get_aircraft_summary(
    connection,
    aircraft_make,
    aircraft_model,
):
    query = """
        SELECT
            COUNT(*) AS report_count,
            COUNT(
                DISTINCT part_name
            ) AS unique_parts,
            COUNT(
                DISTINCT jasc_code
            ) AS unique_jasc_codes,
            MIN(
                difficulty_date
            ) AS first_report_date,
            MAX(
                difficulty_date
            ) AS latest_report_date
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
    query = """
        SELECT
            substr(
                difficulty_date,
                1,
                7
            ) AS month,
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


def get_reports_for_aircraft(
    connection,
    aircraft_make,
    aircraft_model,
    limit=100,
):
    query = """
        SELECT
            r.difficulty_date,
            r.jasc_code,
            COALESCE(
                j.code_name,
                'Unknown JASC code'
            ) AS jasc_name,
            COALESCE(
                c.category_name,
                'Unknown category'
            ) AS jasc_category,
            r.part_name,
            r.part_condition,
            r.discrepancy
        FROM maintenance_reports AS r
        LEFT JOIN jasc_codes AS j
            ON r.jasc_code = j.jasc_code
        LEFT JOIN jasc_categories AS c
            ON substr(
                r.jasc_code,
                1,
                2
            ) = c.category_code
        WHERE r.aircraft_make = ?
          AND r.aircraft_model = ?
        ORDER BY r.difficulty_date DESC
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


def get_jasc_codes_for_aircraft(
    connection,
    aircraft_make,
    aircraft_model,
):
    query = """
        SELECT
            r.jasc_code,
            COALESCE(
                j.code_name,
                'Unknown JASC code'
            ) AS code_name,
            COALESCE(
                c.category_name,
                'Unknown category'
            ) AS category_name,
            COUNT(*) AS report_count
        FROM maintenance_reports AS r
        LEFT JOIN jasc_codes AS j
            ON r.jasc_code = j.jasc_code
        LEFT JOIN jasc_categories AS c
            ON substr(
                r.jasc_code,
                1,
                2
            ) = c.category_code
        WHERE r.aircraft_make = ?
          AND r.aircraft_model = ?
        GROUP BY
            r.jasc_code,
            j.code_name,
            c.category_name
        ORDER BY
            report_count DESC,
            r.jasc_code
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
    query = """
        SELECT
            r.difficulty_date,
            r.jasc_code,
            COALESCE(
                j.code_name,
                'Unknown JASC code'
            ) AS jasc_name,
            COALESCE(
                c.category_name,
                'Unknown category'
            ) AS jasc_category,
            r.part_name,
            r.part_condition,
            r.discrepancy
        FROM maintenance_reports AS r
        LEFT JOIN jasc_codes AS j
            ON r.jasc_code = j.jasc_code
        LEFT JOIN jasc_categories AS c
            ON substr(
                r.jasc_code,
                1,
                2
            ) = c.category_code
        WHERE r.aircraft_make = ?
          AND r.aircraft_model = ?
    """

    params = [
        aircraft_make,
        aircraft_model,
    ]

    if search_text:
        query += """
          AND r.discrepancy LIKE ?
        """

        params.append(
            f"%{search_text}%"
        )

    if jasc_code:
        query += """
          AND r.jasc_code = ?
        """

        params.append(
            jasc_code
        )

    query += """
        ORDER BY r.difficulty_date DESC
        LIMIT ?
    """

    params.append(limit)

    return pd.read_sql_query(
        query,
        connection,
        params=params,
    )


def main():
    with sqlite3.connect(
        database_file
    ) as connection:
        print("Total reports")
        print(
            get_total_reports(
                connection
            )
        )

        print()
        print("Top aircraft makes")
        print(
            get_top_aircraft_makes(
                connection
            )
        )

        print()
        print("Top Boeing models")
        print(
            get_models_for_make(
                connection,
                "BOEING",
            ).head(10)
        )

        print()
        print("Top parts")
        print(
            get_top_parts(
                connection
            )
        )

        print()
        print("Reports by month")
        print(
            get_reports_by_month(
                connection
            )
        )


if __name__ == "__main__":
    main()