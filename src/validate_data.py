import pandas as pd

# load the raw faa dataset
df = pd.read_csv(
    "data/raw/SDR-2025.csv",
    dtype={"JASCCode": "string"},
    low_memory=False,
)


# check for rows that are completely duplicated
duplicate_rows = df.duplicated().sum()

print("\n=== DUPLICATE ROWS ===")
print("Full duplicate rows:", duplicate_rows)


# check if operator control numbers are actually unique
control_number_duplicates = df["OperatorControlNumber"].duplicated().sum()

print("\n=== OPERATOR CONTROL NUMBER ===")
print("Duplicate control numbers:", control_number_duplicates)
print("Unique control numbers:", df["OperatorControlNumber"].nunique())


# try converting the difficulty date column into dates
parsed_dates = pd.to_datetime(
    df["DifficultyDate"],
    format="%m/%d/%Y",
    errors="coerce",
)

# any value that could not be converted becomes NaT
invalid_dates = parsed_dates.isna().sum()

print("\n=== DIFFICULTY DATE ===")
print("Invalid dates:", invalid_dates)


# jasc codes should be four digits
valid_jasc = df["JASCCode"].str.fullmatch(r"\d{4}", na=False)
invalid_jasc = ~valid_jasc

print("\n=== JASC CODE VALIDATION ===")
print("Invalid JASC codes:", invalid_jasc.sum())

# print bad codes if there are any
if invalid_jasc.sum() > 0:
    print("\nInvalid JASC values:")
    print(df.loc[invalid_jasc, "JASCCode"].value_counts().head(20))


# fields that the first version of the app will probably use
core_columns = [
    "OperatorControlNumber",
    "DifficultyDate",
    "JASCCode",
    "AircraftMake",
    "AircraftModel",
    "PartName",
    "PartCondition",
    "StageOfOperationCode",
    "HowDiscoveredCode",
    "Discrepancy",
]

print("\n=== CORE FIELD MISSING VALUES ===")
print(df[core_columns].isna().sum())


# check how long the maintenance descriptions usually are
discrepancy_length = df["Discrepancy"].str.len()

print("\n=== DISCREPANCY LENGTH ===")
print(discrepancy_length.describe())


# check if any discrepancy descriptions are empty strings
empty_discrepancies = df["Discrepancy"].str.strip().eq("").sum()

print("\n=== EMPTY DISCREPANCIES ===")
print("Empty discrepancy descriptions:", empty_discrepancies)


# check the range of difficulty dates after conversion
print("\n=== DATE RANGE ===")
print("Earliest date:", parsed_dates.min())
print("Latest date:", parsed_dates.max())
