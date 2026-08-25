import sqlite3
from pathlib import Path

import pandas as pd

clean_file = Path(
    "data/processed/sdr_2025_clean.csv"
)

database_file = Path(
    "data/aeromaintain.db"
)

jasc_codes_file = Path(
    "data/reference/jasc_codes.csv"
)

jasc_categories_file = Path(
    "data/reference/jasc_categories.csv"
)


database_columns = [
    "operator_control_number",
    "difficulty_date",
    "submission_date",
    "jasc_code",
    "registry_number",
    "aircraft_make",
    "aircraft_model",
    "aircraft_serial_number",
    "aircraft_total_time",
    "aircraft_total_cycles",
    "part_make",
    "part_name",
    "part_number",
    "part_condition",
    "part_location",
    "stage_of_operation_code",
    "how_discovered_code",
    "discrepancy",
]


def create_reports_table(connection):
    connection.execute(
        """
        DROP TABLE IF EXISTS maintenance_reports
        """
    )

    connection.execute(
        """
        CREATE TABLE maintenance_reports (
            operator_control_number TEXT PRIMARY KEY,
            difficulty_date TEXT NOT NULL,
            submission_date TEXT NOT NULL,
            jasc_code TEXT NOT NULL,
            registry_number TEXT,
            aircraft_make TEXT,
            aircraft_model TEXT,
            aircraft_serial_number TEXT,
            aircraft_total_time REAL,
            aircraft_total_cycles REAL,
            part_make TEXT,
            part_name TEXT NOT NULL,
            part_number TEXT,
            part_condition TEXT NOT NULL,
            part_location TEXT,
            stage_of_operation_code TEXT NOT NULL,
            how_discovered_code TEXT NOT NULL,
            discrepancy TEXT NOT NULL
        )
        """
    )


def create_jasc_tables(connection):
    connection.execute(
        """
        DROP TABLE IF EXISTS jasc_codes
        """
    )

    connection.execute(
        """
        DROP TABLE IF EXISTS jasc_categories
        """
    )

    connection.execute(
        """
        CREATE TABLE jasc_categories (
            category_code TEXT PRIMARY KEY,
            category_name TEXT NOT NULL
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE jasc_codes (
            jasc_code TEXT PRIMARY KEY,
            code_name TEXT NOT NULL,
            code_desc TEXT
        )
        """
    )


def create_indexes(connection):
    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_reports_aircraft
        ON maintenance_reports (
            aircraft_make,
            aircraft_model
        )
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_reports_date
        ON maintenance_reports (
            difficulty_date
        )
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_reports_jasc
        ON maintenance_reports (
            jasc_code
        )
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_reports_part
        ON maintenance_reports (
            part_name
        )
        """
    )


def load_reports(connection, df):
    database_df = (
        df.astype(object)
        .where(pd.notna(df), None)
    )

    insert_sql = """
        INSERT INTO maintenance_reports (
            operator_control_number,
            difficulty_date,
            submission_date,
            jasc_code,
            registry_number,
            aircraft_make,
            aircraft_model,
            aircraft_serial_number,
            aircraft_total_time,
            aircraft_total_cycles,
            part_make,
            part_name,
            part_number,
            part_condition,
            part_location,
            stage_of_operation_code,
            how_discovered_code,
            discrepancy
        )
        VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    """

    rows = database_df[
        database_columns
    ].itertuples(
        index=False,
        name=None,
    )

    connection.executemany(
        insert_sql,
        rows,
    )


def load_jasc_categories(connection, df):
    insert_sql = """
        INSERT INTO jasc_categories (
            category_code,
            category_name
        )
        VALUES (?, ?)
    """

    rows = df[
        [
            "category_code",
            "category_name",
        ]
    ].itertuples(
        index=False,
        name=None,
    )

    connection.executemany(
        insert_sql,
        rows,
    )


def load_jasc_codes(connection, df):
    database_df = (
        df.astype(object)
        .where(pd.notna(df), None)
    )

    insert_sql = """
        INSERT INTO jasc_codes (
            jasc_code,
            code_name,
            code_desc
        )
        VALUES (?, ?, ?)
    """

    rows = database_df[
        [
            "jasc_code",
            "code_name",
            "code_desc",
        ]
    ].itertuples(
        index=False,
        name=None,
    )

    connection.executemany(
        insert_sql,
        rows,
    )


def build_database():
    reports_df = pd.read_csv(
        clean_file,
        dtype={"JASCCode": "string"},
        low_memory=False,
    )

    reports_df = reports_df.rename(
        columns={
            "OperatorControlNumber":
                "operator_control_number",
            "DifficultyDate":
                "difficulty_date",
            "SubmissionDate":
                "submission_date",
            "JASCCode":
                "jasc_code",
            "RegistryNNumber":
                "registry_number",
            "AircraftMake":
                "aircraft_make",
            "AircraftModel":
                "aircraft_model",
            "AircraftSerialNumber":
                "aircraft_serial_number",
            "AircraftTotalTime":
                "aircraft_total_time",
            "AircraftTotalCycles":
                "aircraft_total_cycles",
            "PartMake":
                "part_make",
            "PartName":
                "part_name",
            "PartNumber":
                "part_number",
            "PartCondition":
                "part_condition",
            "PartLocation":
                "part_location",
            "StageOfOperationCode":
                "stage_of_operation_code",
            "HowDiscoveredCode":
                "how_discovered_code",
            "Discrepancy":
                "discrepancy",
        }
    )

    jasc_categories_df = pd.read_csv(
        jasc_categories_file,
        dtype={"category_code": "string"},
    )

    jasc_codes_df = pd.read_csv(
        jasc_codes_file,
        dtype={"jasc_code": "string"},
    )

    with sqlite3.connect(
        database_file
    ) as connection:
        create_reports_table(connection)

        load_reports(
            connection,
            reports_df,
        )

        create_jasc_tables(connection)

        load_jasc_categories(
            connection,
            jasc_categories_df,
        )

        load_jasc_codes(
            connection,
            jasc_codes_df,
        )

        create_indexes(connection)

        connection.commit()

        report_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM maintenance_reports
            """
        ).fetchone()[0]

        jasc_code_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM jasc_codes
            """
        ).fetchone()[0]

        category_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM jasc_categories
            """
        ).fetchone()[0]

    print(
        f"Reports inserted: {report_count:,}"
    )

    print(
        f"JASC codes inserted: {jasc_code_count:,}"
    )

    print(
        f"JASC categories inserted: "
        f"{category_count:,}"
    )

    print(
        f"Database saved to: {database_file}"
    )


if __name__ == "__main__":
    build_database()