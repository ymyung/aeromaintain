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