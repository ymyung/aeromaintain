from pathlib import Path

import pandas as pd

# file locations
raw_file = Path("data/raw/SDR-2025.csv")
output_file = Path("data/processed/sdr_2025_clean.csv")


# fields used by the first version of aeromaintain
columns_to_keep = [
    "OperatorControlNumber",
    "DifficultyDate",
    "SubmissionDate",
    "JASCCode",
    "RegistryNNumber",
    "AircraftMake",
    "AircraftModel",
    "AircraftSerialNumber",
    "AircraftTotalTime",
    "AircraftTotalCycles",
    "PartMake",
    "PartName",
    "PartNumber",
    "PartCondition",
    "PartLocation",
    "StageOfOperationCode",
    "HowDiscoveredCode",
    "Discrepancy",
]


# fields where leading/trailing spaces should be removed
text_columns = [
    "OperatorControlNumber",
    "JASCCode",
    "RegistryNNumber",
    "AircraftMake",
    "AircraftModel",
    "AircraftSerialNumber",
    "PartMake",
    "PartName",
    "PartNumber",
    "PartCondition",
    "PartLocation",
    "StageOfOperationCode",
    "HowDiscoveredCode",
]


# categorical fields that should use consistent capitalization
uppercase_columns = [
    "JASCCode",
    "AircraftMake",
    "AircraftModel",
    "PartMake",
    "PartCondition",
    "StageOfOperationCode",
    "HowDiscoveredCode",
]


def clean_data(df):
    # only keep the fields needed by the first version
    clean_df = df[columns_to_keep].copy()

    # convert date fields
    clean_df["DifficultyDate"] = pd.to_datetime(
        clean_df["DifficultyDate"],
        format="%m/%d/%Y",
        errors="coerce",
    )

    clean_df["SubmissionDate"] = pd.to_datetime(
        clean_df["SubmissionDate"],
        errors="coerce",
        utc=True,
    )

    # clean up categorical/text fields
    for column in text_columns:
        clean_df[column] = clean_df[column].str.strip()
        clean_df[column] = clean_df[column].replace("", pd.NA)

    for column in uppercase_columns:
        clean_df[column] = clean_df[column].str.upper()

    # keep the original wording of the maintenance description
    clean_df["Discrepancy"] = clean_df["Discrepancy"].str.strip()

    # make sure cleaning did not remove reports
    if len(clean_df) != len(df):
        raise ValueError("Row count changed during cleaning")

    # control number should still identify one report
    if clean_df["OperatorControlNumber"].duplicated().any():
        raise ValueError("Duplicate OperatorControlNumber found after cleaning")

    return clean_df


def main():
    # load the original faa dataset
    df = pd.read_csv(
        raw_file,
        dtype={"JASCCode": "string"},
        low_memory=False,
    )

    clean_df = clean_data(df)

    print("\n=== CLEANING SUMMARY ===")
    print("Raw shape:", df.shape)
    print("Cleaned shape:", clean_df.shape)

    print("\nMissing aircraft makes:")
    print(clean_df["AircraftMake"].isna().sum())

    print("\nMissing aircraft models:")
    print(clean_df["AircraftModel"].isna().sum())

    print("\nDuplicate control numbers:")
    print(clean_df["OperatorControlNumber"].duplicated().sum())

    print("\nInvalid difficulty dates:")
    print(clean_df["DifficultyDate"].isna().sum())

    print("\nInvalid submission dates:")
    print(clean_df["SubmissionDate"].isna().sum())

    print("\nEmpty discrepancy descriptions:")
    print(clean_df["Discrepancy"].str.strip().eq("").sum())

    # save the processed dataset
    clean_df.to_csv(
        output_file,
        index=False,
    )

    print("\nCleaned dataset saved to:")
    print(output_file)


if __name__ == "__main__":
    main()
