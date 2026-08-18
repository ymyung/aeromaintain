# Data Notes

## Source

The data comes from the FAA Service Difficulty Reports (SDR). For now, I am using the 2025 dataset.

* File: `SDR-2025.csv`
* Number of reports: 67,620
* Number of columns: 76

The initial inspection is done using `src/inspect_data.py` with pandas.

## Initial Inspection

The dataset is much larger than I expected and contains a lot of information about each maintenance report. This includes aircraft make/model, dates, affected parts, aircraft operating information, JASC codes, and a written description of the maintenance problem.

A lot of the columns are very incomplete, especially fields related to propellers, components, engines, and detailed structural locations. However, some of the fields that seem most useful for this project have very good coverage.

The `Discrepancy` column looks especially useful because every report has one and most of the descriptions are unique.

* Missing discrepancy values: 0
* Unique discrepancy values: 65,645

The descriptions also contain a lot of actual maintenance information, so this could potentially be used later for machine learning.

---

## Fields That Look Useful

### DifficultyDate

* 0 missing values
* 365 unique values

This should be useful for displaying reports over time and filtering by date.

### JASCCode

* 0 missing values
* 436 unique codes

The most common codes are:

* 5320: 8,540 reports
* 3350: 7,824 reports
* 2560: 3,264 reports
* 5210: 3,095 reports
* 5347: 2,936 reports

I need to research exactly how JASC codes are structured before using them.

There are probably too many codes to directly use all 436 as ML classes, but it may be possible to group them into larger aircraft systems.

### AircraftMake

* 84 missing values
* 56 unique values

Most common manufacturers:

* BOEING: 34,418
* AIRBUS: 16,954
* CNDAIR: 6,408
* EMB: 5,138
* CESSNA: 1,347

This field should be useful for one of the main dashboard filters.

### AircraftModel

* 88 missing values
* 518 unique values

Some of the most common models are:

* 7377H4: 4,921
* 737823: 3,951
* 7378H4: 2,813
* CL6002D24: 2,388
* CL6002C10: 2,203
* ERJ170200LR: 2,135

There are a lot of different aircraft variants. I need to figure out whether these should stay separate or if some should eventually be grouped into aircraft families.

### PartName

* 0 missing values
* 1,195 unique values

This seems useful for looking at what parts are most commonly mentioned in reports.

### PartCondition

* 0 missing values
* 290 unique values

This could also be useful, but I need to inspect the actual values to see whether there are similar conditions that should be grouped together.

### PartLocation

* 1,305 missing values
* About 1.9% missing

This has much better coverage than a lot of the other part/component fields, so it might be useful later.

### StageOfOperationCode

* 0 missing values
* 15 unique values

This could potentially be used to show when problems were discovered, such as during flight, inspection, maintenance, etc.

I still need to look up what each code means.

### HowDiscoveredCode

* 0 missing values
* 13 unique values

This could also be useful for understanding how maintenance issues are normally found.

### ComponentName

* 66,878 missing values
* Around 98.9% missing

This field is probably too incomplete to use as one of the main fields in the application.

### Discrepancy

* 0 missing values
* 65,645 unique values

This is probably one of the most important fields in the dataset.

It contains descriptions of the maintenance problem and often also explains what maintenance was performed.

Some examples I saw involved:

* elevator hinge problems
* unsafe landing gear indications
* cracks in aircraft skin
* wing corrosion
* sensor replacements
* maintenance manual references

The descriptions usually contain enough information that a person could probably identify which aircraft system the problem is related to.

Because of this, I want to investigate using this column for text classification later.

---

## Missing Data

There is a huge difference in how complete each column is.

Some columns are almost completely empty.

Examples:

* `PrecautionaryProcedureD`: ~99.99% missing
* `PropellerTotalCycles`: ~99.98% missing
* `PrecautionaryProcedureC`: ~99.95% missing
* `PropellerTotalTime`: ~99.90% missing
* `ComponentModel`: ~99.89% missing
* `ComponentName`: ~98.90% missing
* `EngineMake`: ~96.92% missing

These probably shouldn't be important parts of the first version of the application.

Some other fields have better coverage but are still incomplete:

* `PartNumber`: ~64% missing
* `PartMake`: ~47% missing
* `PartLocation`: ~2% missing

The main fields I am considering using have much better coverage:

* `DifficultyDate`: 0% missing
* `JASCCode`: 0% missing
* `PartName`: 0% missing
* `PartCondition`: 0% missing
* `StageOfOperationCode`: 0% missing
* `HowDiscoveredCode`: 0% missing
* `Discrepancy`: 0% missing
* `AircraftMake`: ~0.12% missing
* `AircraftModel`: ~0.13% missing

---

## Mixed Data Types

Pandas gave a `DtypeWarning` when reading the CSV.

The affected columns were:

* `PrecautionaryProcedureC`
* `PrecautionaryProcedureD`
* `StringerTo`
* `ButtlineTo`
* `WaterLineTo`

I inspected a few of the values.

`PrecautionaryProcedureC` and `PrecautionaryProcedureD` mostly appear to contain letter codes such as:

* A
* I
* K
* O

The structural location fields contain both numbers and text.

Examples:

`StringerTo`

* 26
* 22
* 29
* BEAM2

`ButtlineTo`

* RIB27
* RIB25
* RBL10
* LBL10
* 36

`WaterLineTo`

* 145.34
* 1805
* 290
* 208

Because some of these values are actual structural identifiers, I don't think it would make sense to automatically convert all of these columns into numbers.

For now I will leave them alone until I understand the fields better.

---

## Aircraft Distribution

One important thing I noticed is that the data is heavily weighted toward Boeing and Airbus.

For example, Boeing alone has over 34,000 reports in the 2025 dataset.

Because of this, I cannot say something like:

> "Boeing aircraft fail more often."

There could simply be more Boeing aircraft operating, more flight hours, or different reporting behaviour.

For the project, I should describe the numbers as:

* number of reports
* reported maintenance issues
* distribution of reports

I should avoid calling them true failure rates unless I later find another dataset that gives a useful denominator such as total flights, fleet size, or flight hours.

---

## Possible Machine Learning Idea

The current idea is to use the maintenance description to predict which aircraft system the report belongs to.

Possible setup:

`Discrepancy` → text processing → classifier → aircraft system/category

The JASC code could potentially be used to create the target labels.

Before doing this I need to:

1. Understand what JASC codes mean.
2. Figure out whether they can be grouped into larger categories.
3. Check how imbalanced the categories are.
4. Check whether the discrepancy text directly gives away the JASC category.
5. Decide which evaluation metric makes sense.

The first model will probably be a simple baseline such as:

TF-IDF + Logistic Regression

After that I can compare it against a small neural network.

I don't want to assume that the neural network will be better. If the simpler model performs just as well or better, that is still a useful result.

---

## Possible Cleaning Steps

These are ideas for now and not final decisions.

* Convert `DifficultyDate` into a proper date type.
* Convert `SubmissionDate` into a proper date/time type.
* Remove unnecessary leading/trailing spaces.
* Investigate inconsistent capitalization.
* Check whether aircraft manufacturer names need normalization.
* Check whether aircraft model names need normalization.
* Keep the original raw dataset unchanged.
* Do not fill missing values unless there is a good reason.
* Keep mixed structural location fields as text for now.
* Check for duplicate reports.
* Check whether `OperatorControlNumber` is unique.
* Only keep fields that actually contribute something useful to the application.

---

## Questions to Investigate

* What does each JASC code mean?
* Is there a standard way to group JASC codes into larger aircraft systems?
* Are the JASC categories balanced enough for machine learning?
* Does the discrepancy text contain information that would create data leakage?
* Is `OperatorControlNumber` unique?
* Are there duplicate reports?
* Are aircraft manufacturer names already standardized?
* How should different versions of the same aircraft model be handled?
* What do the `StageOfOperationCode` values mean?
* What do the `HowDiscoveredCode` values mean?
* Which part fields are actually useful despite missing data?
* Should the first version use only 2025 or combine multiple years?

---

## Current Direction

Based on the first inspection, the fields that currently seem most useful are:

* `OperatorControlNumber`
* `DifficultyDate`
* `JASCCode`
* `AircraftMake`
* `AircraftModel`
* `PartName`
* `PartCondition`
* `PartLocation`
* `StageOfOperationCode`
* `HowDiscoveredCode`
* `Discrepancy`

The next step is to understand what these coded fields mean and check the data for duplicates and inconsistencies before I start cleaning it or designing the database.
