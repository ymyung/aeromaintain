import pandas as pd

# file locations
raw_file = "data/raw/SDR-2025.csv"
output_file = "data/processed/sdr_2025_clean.csv"


# load the original faa data
df = pd.read_csv(
    raw_file,
    dtype={"JASCCode": "string"},
    low_memory=False,
)


# fields that are useful for the first version of aeromaintain
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


# make a separate dataframe so the raw data is left alone
clean_df = df[columns_to_keep].copy()


# convert the difficulty date into an actual date
clean_df["DifficultyDate"] = pd.to_datetime(
    clean_df["DifficultyDate"],
    format="%m/%d/%Y",
    errors="coerce",
)


# convert submission timestamps to datetime
# utc=True handles the timezone information included in the faa data
clean_df["SubmissionDate"] = pd.to_datetime(
    clean_df["SubmissionDate"],
    errors="coerce",
    utc=True,
)


# text fields where extra spaces would not have any useful meaning
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


# remove spaces at the beginning and end of text values
for column in text_columns:
    clean_df[column] = clean_df[column].str.strip()


# turn empty strings into proper missing values
for column in text_columns:
    clean_df[column] = clean_df[column].replace("", pd.NA)


# keep category fields consistent
# these values are identifiers/categories rather than normal sentences
uppercase_columns = [
    "JASCCode",
    "AircraftMake",
    "AircraftModel",
    "PartMake",
    "PartCondition",
    "StageOfOperationCode",
    "HowDiscoveredCode",
]


for column in uppercase_columns:
    clean_df[column] = clean_df[column].str.upper()


# only remove extra spaces from the beginning and end of discrepancy text
# don't change capitalization or wording because we may use this for ml later
clean_df["Discrepancy"] = clean_df["Discrepancy"].str.strip()


# basic checks before saving the cleaned dataset
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


# make sure cleaning did not accidentally remove any reports
if len(clean_df) != len(df):
    raise ValueError("Row count changed during cleaning")


# make sure the report identifier is still unique
if clean_df["OperatorControlNumber"].duplicated().any():
    raise ValueError("Duplicate OperatorControlNumber found after cleaning")


# save the processed dataset
clean_df.to_csv(
    output_file,
    index=False,
)

print("\nCleaned dataset saved to:")
print(output_file)
