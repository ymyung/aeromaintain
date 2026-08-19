# AeroMaintain

AeroMaintain is a project for exploring aircraft maintenance data from the FAA Service Difficulty Report (SDR) dataset.

The goal is to build a simple application that makes it easier to look at maintenance reports by aircraft, part, date, and system. I also plan to test whether the maintenance descriptions can be used for machine learning classification.

## Current Status

The project is currently in development.

Completed so far:

- explored the 2025 FAA SDR dataset
- validated report IDs, dates, JASC codes, and important fields
- documented missing data and data quality issues
- built an initial cleaning pipeline
- preserved the original raw dataset separately from processed data
- added automated tests for the cleaning pipeline

## Dataset

Current dataset:

- FAA Service Difficulty Reports, 2025
- 67,620 maintenance reports
- 76 original fields
- 18 fields currently kept in the processed dataset

Some of the main fields being used are:

- aircraft make and model
- JASC code
- part name and condition
- date of maintenance issue
- maintenance discrepancy description

The project currently uses report counts and reported maintenance issues rather than claiming these represent actual aircraft failure rates.

## Project Structure

```text
aeromaintain/
├── data/
│   ├── raw/
│   └── processed/
├── docs/
├── screenshots/
├── src/
│   ├── inspect_data.py
│   ├── validate_data.py
│   └── clean_data.py
├── tests/
└── test_clean_data.py
└── README.md