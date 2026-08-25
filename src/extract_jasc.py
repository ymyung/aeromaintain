import re
from pathlib import Path

import pandas as pd
from pypdf import PdfReader

source_file = Path("data/reference/source/JASC_Code.pdf")
codes_file = Path("data/reference/jasc_codes.csv")
categories_file = Path("data/reference/jasc_categories.csv")
clean_file = Path("data/processed/sdr_2025_clean.csv")

# indexes 7 through 12 contain the compact JASC reference table
quick_reference_pages = range(7, 13)

# detailed definitions begin at index 13
definition_pages = range(13, 73)


category_pattern = re.compile(r"^(\d{2})\s+(.+)$")
code_pattern = re.compile(r"^(\d{4})\s+(.+)$")
definition_category_pattern = re.compile(r"^(\d{2})\s*-\s*(.+)$")


def extract_quick_reference(reader):
    categories = []
    codes = []

    for page_number in quick_reference_pages:
        text = reader.pages[page_number].extract_text()

        if not text:
            continue

        for line in text.splitlines():
            cleaned_line = line.strip()

            category_match = category_pattern.match(cleaned_line)
            code_match = code_pattern.match(cleaned_line)

            if category_match:
                category_code = category_match.group(1)
                category_name = category_match.group(2).strip()

                categories.append(
                    {
                        "category_code": category_code,
                        "category_name": category_name,
                    }
                )

            elif code_match:
                jasc_code = code_match.group(1)
                code_name = code_match.group(2).strip()

                codes.append(
                    {
                        "jasc_code": jasc_code,
                        "code_name": code_name,
                    }
                )

    return categories, codes


def extract_descriptions(reader, valid_codes):
    descriptions = {}

    current_code = None
    description_lines = []

    def save_description():
        if current_code is None:
            return

        description = " ".join(description_lines).strip()

        if description:
            descriptions[current_code] = description

    for page_number in definition_pages:
        text = reader.pages[page_number].extract_text()

        if not text:
            continue

        for line in text.splitlines():
            cleaned_line = line.strip()

            # ignore repeated document headings
            if cleaned_line in {
                "SYSTEM CODES - TITLE",
                "DEFINITIONS",
                "AIRCRAFT",
            }:
                continue

            # category headings separate groups of detailed definitions
            if definition_category_pattern.match(cleaned_line):
                save_description()

                current_code = None
                description_lines = []

                continue

            code_match = code_pattern.match(cleaned_line)

            # only accept codes already found in the quick-reference table
            if code_match and code_match.group(1) in valid_codes:
                save_description()

                current_code = code_match.group(1)
                description_lines = []

                continue

            if current_code and cleaned_line:
                description_lines.append(cleaned_line)

    # save the final description in the document
    save_description()

    return descriptions


def build_reference_data():
    reader = PdfReader(source_file)

    categories, codes = extract_quick_reference(reader)

    categories_df = pd.DataFrame(categories)
    codes_df = pd.DataFrame(codes)

    # remove any accidental duplicate records
    categories_df = categories_df.drop_duplicates(
        subset="category_code",
    )

    codes_df = codes_df.drop_duplicates(
        subset="jasc_code",
    )

    # sort so the generated files are predictable and easy to inspect
    categories_df = categories_df.sort_values(
        "category_code",
    ).reset_index(drop=True)

    codes_df = codes_df.sort_values(
        "jasc_code",
    ).reset_index(drop=True)

    valid_codes = set(codes_df["jasc_code"])

    descriptions = extract_descriptions(
        reader,
        valid_codes,
    )

    # add detailed descriptions to the quick-reference code table
    codes_df["code_desc"] = codes_df["jasc_code"].map(descriptions).fillna("")

    return categories_df, codes_df


def validate_reference_data(categories_df, codes_df):
    # category codes should always contain exactly 2 digits
    valid_categories = categories_df["category_code"].str.fullmatch(r"\d{2}")

    if not valid_categories.all():
        raise ValueError("Invalid JASC category code found")

    # JASC codes should always contain exactly 4 digits
    valid_codes = codes_df["jasc_code"].str.fullmatch(r"\d{4}")

    if not valid_codes.all():
        raise ValueError("Invalid JASC code found")

    # codes and categories should each be unique
    if categories_df["category_code"].duplicated().any():
        raise ValueError("Duplicate JASC category found")

    if codes_df["jasc_code"].duplicated().any():
        raise ValueError("Duplicate JASC code found")

    # every code should belong to a known category
    known_categories = set(categories_df["category_code"])

    code_categories = codes_df["jasc_code"].str[:2]

    missing_categories = sorted(set(code_categories) - known_categories)

    if missing_categories:
        raise ValueError(
            f"JASC codes reference missing categories: {missing_categories}"
        )


def validate_sdr_coverage(codes_df):
    if not clean_file.exists():
        print()
        print("Clean SDR dataset not found.")
        print("Skipping SDR JASC coverage check.")

        return

    reports = pd.read_csv(
        clean_file,
        dtype={"JASCCode": "string"},
        usecols=["JASCCode"],
    )

    dataset_codes = set(reports["JASCCode"].dropna().str.strip())

    reference_codes = set(codes_df["jasc_code"])

    missing_codes = sorted(dataset_codes - reference_codes)

    print()
    print(f"JASC codes used by SDR dataset: {len(dataset_codes)}")
    print(
        f"Dataset codes found in reference: {len(dataset_codes) - len(missing_codes)}"
    )

    if missing_codes:
        print("Dataset codes missing from reference:")

        print(missing_codes)
    else:
        print("All SDR JASC codes exist in the reference table.")


def main():
    categories_df, codes_df = build_reference_data()

    validate_reference_data(
        categories_df,
        codes_df,
    )

    categories_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    categories_df.to_csv(
        categories_file,
        index=False,
    )

    codes_df.to_csv(
        codes_file,
        index=False,
    )

    print("JASC reference extraction complete.")
    print(f"Categories: {len(categories_df)}")
    print(f"Codes: {len(codes_df)}")

    descriptions_found = codes_df["code_desc"].str.strip().ne("").sum()

    print(f"Codes with descriptions: {descriptions_found}")

    print()
    print(f"Saved: {categories_file}")
    print(f"Saved: {codes_file}")

    validate_sdr_coverage(codes_df)


if __name__ == "__main__":
    main()
