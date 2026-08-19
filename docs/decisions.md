# Engineering Decisions

## 2026-08-18 - start with the 2025 SDR dataset

### Decision
Use the complete 2025 FAA SDR dataset as the first dataset for development.

### Reason
Using one complete year keeps the first version manageable while still providing 67,620 reports to work with. It also makes it easier to understand the data before combining multiple years.

### Alternative considered
Import multiple years immediately.

### Tradeoff
The first version will not be able to show long-term trends until more years are added.


## 2026-08-18 - keep the raw dataset unchanged

### Decision
Keep the original FAA CSV unchanged and perform all cleaning through Python scripts.

### Reason
This makes the data processing reproducible and lets me trace cleaned data back to the original source.

### Alternative considered
Manually clean or modify the CSV before using it.

### Tradeoff
The cleaning pipeline will take more work to build, but changes to the data will be easier to track and reproduce.


## 2026-08-18 - report counts are not failure rates

### Decision
The application will describe results as maintenance report counts or reported issues instead of aircraft failure rates.

### Reason
The SDR data does not include enough information about fleet size, number of flights, or flight hours to calculate a fair failure rate between aircraft.

### Alternative considered
Compare aircraft based directly on the number of reports.

### Tradeoff
This limits some of the reliability comparisons that can be made, but avoids making conclusions that the data cannot support.


## 2026-08-18 - investigate JASC codes before choosing the ML target

### Decision
Do not define the final machine learning classification problem until the JASC code structure and class distribution have been investigated.

### Reason
There are 436 JASC codes in the 2025 dataset. Predicting all of them may be too specific and the classes may be heavily imbalanced.

### Alternative considered
Immediately use all 436 JASC codes as classification labels.

### Tradeoff
ML development starts later, but the final classification problem should be more meaningful and easier to justify.


## 2026-08-18 - do not automatically convert mixed structural fields to numbers

### Decision
Leave fields such as `StringerTo`, `ButtlineTo`, and `WaterLineTo` unchanged until their meaning is better understood.

### Reason
The columns contain both numeric-looking values and identifiers such as `BEAM2`, `RIB27`, and `RBL10`. Converting the columns directly to numeric values could destroy valid information.

### Alternative considered
Force the mixed-type columns to numeric values and treat anything else as missing.

### Tradeoff
The fields will require more investigation before they can be used for analysis.


## 2026-08-18 - validate the data before cleaning it

### Decision
Create a separate validation step before making any changes to the raw dataset.

### Reason
I want to check assumptions such as duplicate reports, date formatting, missing core fields, and JASC code formatting before deciding how the cleaning pipeline should handle them.

### Alternative considered
Start cleaning the dataset immediately based on the initial inspection.

### Tradeoff
This adds another step before building the application, but it should prevent me from removing or changing valid data without understanding it first.


## 2026-08-18 - treat JASC codes as strings

### Decision
Import `JASCCode` as a string instead of a numeric value.

### Reason
JASC codes are identifiers rather than quantities. Treating them as numbers could imply relationships between codes that do not actually exist and could also cause problems if formatting such as leading zeroes matters.

### Alternative considered
Allow pandas to automatically infer JASC codes as numbers.

### Tradeoff
Any numerical operations would require conversion later, but I do not currently expect numerical calculations on the codes themselves.


## 2026-08-18 - use OperatorControlNumber as the report identifier

### Decision
Use `OperatorControlNumber` as the main identifier for maintenance reports in the cleaned dataset.

### Reason
Validation showed that all 67,620 records have an OperatorControlNumber and there are no duplicate values in the 2025 dataset.

### Alternative considered
Create a new generated ID for every report.

### Tradeoff
The FAA identifier is useful for tracing cleaned records back to the source data, although I may still use a database-generated ID later if it makes database design easier.


## 2026-08-18 - do not remove rows with missing aircraft make or model

### Decision
Keep reports that are missing `AircraftMake` or `AircraftModel`.

### Reason
Only 84 records are missing aircraft make and 88 are missing aircraft model. The reports still contain other useful information such as JASC code, part information, and discrepancy text.

### Alternative considered
Drop any record that does not have both aircraft make and aircraft model.

### Tradeoff
Some dashboard filters will need to handle missing aircraft information, but useful maintenance reports will not be unnecessarily removed.


## 2026-08-18 - parse DifficultyDate during cleaning

### Decision
Parse `DifficultyDate` as a proper date during the cleaning process.

### Reason
All 67,620 dates were successfully parsed using the expected month/day/year format and the date range matches the 2025 dataset.

### Alternative considered
Keep the dates as strings.

### Tradeoff
The cleaning pipeline needs to enforce a specific date format, but parsing the field will make filtering and time-based analysis much easier later.


## 2026-08-18 - standardize submission timestamps to UTC

### Decision
Parse `SubmissionDate` as a datetime and standardize the timestamps to UTC during cleaning.

### Reason
The FAA submission timestamps include timezone information. Converting them to one consistent timezone should make sorting and comparing submission times easier later.

### Alternative considered
Keep the original timestamp strings exactly as they appear in the CSV.

### Tradeoff
The processed timestamp will no longer display the original timezone offset, but the actual point in time is preserved in a consistent format.


## 2026-08-18 - keep discrepancy text for machine learning and analysis

### Decision
Keep the full `Discrepancy` text in the cleaned dataset.

### Reason
Every report contains a non-empty discrepancy description. The median description is 203 characters long, so the field contains enough text to be useful for search, analysis, and possible machine learning.

### Alternative considered
Only keep structured fields such as JASC code and part name.

### Tradeoff
Keeping free text increases storage and requires additional preprocessing for machine learning, but it preserves one of the most informative fields in the dataset.


## 2026-08-18 - keep cleaning conservative

### Decision
Only apply cleaning rules that are supported by the data inspection and validation results.

### Reason
The FAA data is already fairly structured and some unusual values may still be valid aircraft or maintenance identifiers. I do not want to change values just to make the dataset look cleaner.

### Alternative considered
Apply broader cleaning such as removing incomplete rows, combining aircraft models, or replacing unusual values automatically.

### Tradeoff
Some inconsistencies may remain in the first version, but there is less risk of changing valid source information.


## 2026-08-18 - reduce the processed dataset to useful fields

### Decision
Create the first processed dataset using 18 fields from the original 76.

### Reason
Many FAA SDR fields are extremely sparse or are not currently needed by the application. Keeping a smaller application-focused dataset makes later database and analytics work simpler while the original CSV remains available if another field is needed.

### Alternative considered
Import all 76 fields into the application database.

### Tradeoff
A field that becomes useful later may need to be added back into the cleaning pipeline, but this avoids carrying a large number of unused fields through the first version.


## 2026-08-18 - preserve original discrepancy wording

### Decision
Only remove leading and trailing whitespace from `Discrepancy` and otherwise preserve the original maintenance description.

### Reason
The discrepancy field contains the original maintenance narrative and may later be used for machine learning. Any model-specific preprocessing should happen separately rather than changing the cleaned source text.

### Alternative considered
Convert all discrepancy text to lowercase or perform text cleaning during the main data-cleaning step.

### Tradeoff
The stored text may contain inconsistent capitalization and formatting, but the original information is preserved.


## 2026-08-18 - preserve row count during initial cleaning

### Decision
The initial cleaning pipeline should keep all 67,620 validated maintenance reports.

### Reason
Validation did not find duplicate reports or invalid core records, and missing aircraft make/model values do not make the rest of a report unusable.

### Alternative considered
Remove incomplete reports during cleaning.

### Tradeoff
Some records will not work with every dashboard filter, but they can still contribute to other analyses.