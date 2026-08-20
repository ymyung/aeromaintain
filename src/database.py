import sqlite3
from pathlib import Path

import pandas as pd

# file locations
clean_file = Path("data/processed/sdr_2025_clean.csv")
database_file = Path("data/aeromaintain.db")


def create_reports_table(connection):
    # rebuild the table each time the database is generated
    connection.execute("DROP TABLE IF EXISTS maintenance_reports")

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


def create_indexes(connection):
    # indexes for fields that will probably be filtered often
    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_reports_aircraft
        ON maintenance_reports (aircraft_make, aircraft_model)
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_reports_date
        ON maintenance_reports (difficulty_date)
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_reports_jasc
        ON maintenance_reports (jasc_code)
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_reports_part
        ON maintenance_reports (part_name)
        """
    )


def load_reports(connection, df):
    # convert pandas missing values into values sqlite can store
    database_df = df.astype(object).where(pd.notna(df), None)

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
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    connection.executemany(
        insert_sql,
        database_df.itertuples(index=False, name=None),
    )


def prepare_database_data(df):
    # use simpler snake_case names inside the database
    return df.rename(
        columns={
            "OperatorControlNumber": "operator_control_number",
            "DifficultyDate": "difficulty_date",
            "SubmissionDate": "submission_date",
            "JASCCode": "jasc_code",
            "RegistryNNumber": "registry_number",
            "AircraftMake": "aircraft_make",
            "AircraftModel": "aircraft_model",
            "AircraftSerialNumber": "aircraft_serial_number",
            "AircraftTotalTime": "aircraft_total_time",
            "AircraftTotalCycles": "aircraft_total_cycles",
            "PartMake": "part_make",
            "PartName": "part_name",
            "PartNumber": "part_number",
            "PartCondition": "part_condition",
            "PartLocation": "part_location",
            "StageOfOperationCode": "stage_of_operation_code",
            "HowDiscoveredCode": "how_discovered_code",
            "Discrepancy": "discrepancy",
        }
    )


def build_database():
    # make sure the cleaned dataset exists first
    if not clean_file.exists():
        raise FileNotFoundError(
            "Cleaned dataset not found. Run src/clean_data.py first."
        )

    # load the processed dataset
    df = pd.read_csv(
        clean_file,
        dtype={"JASCCode": "string"},
        low_memory=False,
    )

    database_df = prepare_database_data(df)

    # make sure the output folder exists
    database_file.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(database_file) as connection:
        create_reports_table(connection)

        # load all reports before building indexes
        load_reports(connection, database_df)

        create_indexes(connection)

        connection.commit()

        report_count = connection.execute(
            "SELECT COUNT(*) FROM maintenance_reports"
        ).fetchone()[0]

        # make sure every processed report made it into the database
        if report_count != len(database_df):
            raise ValueError(
                f"Expected {len(database_df)} reports but database has {report_count}"
            )

    print("\n=== DATABASE BUILD ===")
    print("Reports inserted:", report_count)
    print("Database:", database_file)


if __name__ == "__main__":
    build_database()