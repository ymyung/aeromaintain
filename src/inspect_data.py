import pandas as pd

# load the 2025 faa maintenance data
df = pd.read_csv("data/raw/SDR-2025.csv")


# show one random report
print(df.sample(1).to_string())

# basic dataset info
print("Dataset shape:", df.shape)
print(df.columns)
print(df.dtypes)

# check which columns have the most missing values
print(df.isna().sum().sort_values(ascending=False))


# columns that gave mixed type warnings
mixed_type_columns = [
    "PrecautionaryProcedureC",
    "PrecautionaryProcedureD",
    "StringerTo",
    "ButtlineTo",
    "WaterLineTo",
]

print("\n=== MIXED TYPE COLUMNS ===")

# look at some real values from each mixed type column
for column in mixed_type_columns:
    print(f"\n{column}")
    print(df[column].dropna().head(10))


# columns that look most useful for the project so far
important_columns = [
    "DifficultyDate",
    "JASCCode",
    "AircraftMake",
    "AircraftModel",
    "PartMake",
    "PartName",
    "PartCondition",
    "ComponentName",
    "StageOfOperationCode",
    "HowDiscoveredCode",
    "Discrepancy",
]

print("\n=== IMPORTANT COLUMN SUMMARY ===")

# check missing values and number of unique values
for column in important_columns:
    missing = df[column].isna().sum()
    unique = df[column].nunique(dropna=True)

    print(f"{column}: {missing} missing, {unique} unique values")


# see which aircraft manufacturers appear most often
print("\n=== TOP AIRCRAFT MAKES ===")
print(df["AircraftMake"].value_counts().head(20))

# see which aircraft models appear most often
print("\n=== TOP AIRCRAFT MODELS ===")
print(df["AircraftModel"].value_counts().head(20))


# inspect jasc code distribution
print("\n=== JASC CODE SUMMARY ===")

print("Unique JASC codes:")
print(df["JASCCode"].nunique())

print("\nMost common JASC codes:")
print(df["JASCCode"].value_counts().head(20))


# read a few actual maintenance descriptions
print("\n=== SAMPLE DISCREPANCIES ===")

for discrepancy in df["Discrepancy"].sample(5):
    print("\n---")
    print(discrepancy)


# calculate missing value counts and percentages
missing_count = df.isna().sum()
missing_percentage = (missing_count / len(df)) * 100

missing_summary = pd.DataFrame(
    {
        "missing_count": missing_count,
        "missing_percentage": missing_percentage,
    }
)

# sort so the worst missing columns show up first
missing_summary = missing_summary.sort_values(
    "missing_percentage",
    ascending=False,
)

print("\n=== MISSING VALUE SUMMARY ===")
print(missing_summary.to_string())
