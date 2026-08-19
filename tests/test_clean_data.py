import pandas as pd
import pytest

from src.clean_data import clean_data, columns_to_keep


# make a small fake dataset for testing
def make_test_data():
    return pd.DataFrame(
        [
            {
                "OperatorControlNumber": " TEST001 ",
                "DifficultyDate": "01/15/2025",
                "SubmissionDate": "2025-01-16T10:30:00-05:00",
                "JASCCode": "5320",
                "RegistryNNumber": " N123AB ",
                "AircraftMake": " boeing ",
                "AircraftModel": " 7378h4 ",
                "AircraftSerialNumber": " ABC123 ",
                "AircraftTotalTime": 12000.0,
                "AircraftTotalCycles": 8000.0,
                "PartMake": " boeing ",
                "PartName": "HINGE",
                "PartNumber": " P123 ",
                "PartCondition": " damaged ",
                "PartLocation": " LEFT WING ",
                "StageOfOperationCode": " in ",
                "HowDiscoveredCode": " o ",
                "Discrepancy": "  Found crack in left wing.  ",
            },
            {
                "OperatorControlNumber": "TEST002",
                "DifficultyDate": "02/20/2025",
                "SubmissionDate": "2025-02-21T14:00:00-05:00",
                "JASCCode": "3350",
                "RegistryNNumber": "N456CD",
                "AircraftMake": None,
                "AircraftModel": None,
                "AircraftSerialNumber": "DEF456",
                "AircraftTotalTime": 5000.0,
                "AircraftTotalCycles": 3000.0,
                "PartMake": None,
                "PartName": "SENSOR",
                "PartNumber": "",
                "PartCondition": "FAILED",
                "PartLocation": "LANDING GEAR",
                "StageOfOperationCode": "IN",
                "HowDiscoveredCode": "O",
                "Discrepancy": "Landing gear unsafe indication.",
            },
        ]
    )


# cleaning should not remove any reports
def test_cleaning_preserves_row_count():
    raw_df = make_test_data()

    cleaned_df = clean_data(raw_df)

    assert len(cleaned_df) == len(raw_df)


# processed data should only contain the fields we decided to keep
def test_only_expected_columns_are_kept():
    raw_df = make_test_data()

    cleaned_df = clean_data(raw_df)

    assert list(cleaned_df.columns) == columns_to_keep


# extra spaces should be removed from text fields
def test_text_fields_are_trimmed():
    cleaned_df = clean_data(make_test_data())

    assert cleaned_df.loc[0, "OperatorControlNumber"] == "TEST001"
    assert cleaned_df.loc[0, "RegistryNNumber"] == "N123AB"
    assert cleaned_df.loc[0, "PartNumber"] == "P123"


# category fields should use consistent capitalization
def test_category_fields_are_uppercase():
    cleaned_df = clean_data(make_test_data())

    assert cleaned_df.loc[0, "AircraftMake"] == "BOEING"
    assert cleaned_df.loc[0, "AircraftModel"] == "7378H4"
    assert cleaned_df.loc[0, "PartCondition"] == "DAMAGED"
    assert cleaned_df.loc[0, "StageOfOperationCode"] == "IN"


# the date columns should be converted from strings
def test_dates_are_converted():
    cleaned_df = clean_data(make_test_data())

    assert pd.api.types.is_datetime64_any_dtype(cleaned_df["DifficultyDate"])
    assert pd.api.types.is_datetime64_any_dtype(cleaned_df["SubmissionDate"])


# blank strings should be treated as missing data
def test_empty_strings_become_missing_values():
    cleaned_df = clean_data(make_test_data())

    assert pd.isna(cleaned_df.loc[1, "PartNumber"])


# reports should stay even if make or model is missing
def test_missing_aircraft_information_is_preserved():
    cleaned_df = clean_data(make_test_data())

    assert pd.isna(cleaned_df.loc[1, "AircraftMake"])
    assert pd.isna(cleaned_df.loc[1, "AircraftModel"])
    assert len(cleaned_df) == 2


# discrepancy wording should stay the same apart from outside spaces
def test_discrepancy_wording_is_preserved():
    cleaned_df = clean_data(make_test_data())

    assert cleaned_df.loc[0, "Discrepancy"] == "Found crack in left wing."


# duplicate report ids should cause the cleaning pipeline to stop
def test_duplicate_control_numbers_raise_error():
    raw_df = make_test_data()

    raw_df.loc[0, "OperatorControlNumber"] = "TEST001"
    raw_df.loc[1, "OperatorControlNumber"] = "TEST001"

    with pytest.raises(ValueError, match="Duplicate OperatorControlNumber"):
        clean_data(raw_df)
