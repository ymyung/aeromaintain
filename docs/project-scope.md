# AeroMaintain Project Scope

## Problem
FAA maintenance data contains a large number of aircraft maintenance reports, but the raw data is difficult to explore directly. This project will provide a simple way to analyze reported maintenance issues by aircraft make, model, part, and time period.

## Intended User
The initial intended user is someone interested in exploring aircraft maintenance data, such as an engineering student, researcher, or aviation enthusiast.

## MVP
The first version should be able to:
- load and clean FAA SDR data
- store useful fields in a database
- filter reports by aircraft make and model
- show common reported parts and maintenance issues
- show how report counts change over time
- allow users to view the original maintenance descriptions

## Non-Goals
For the first version, the project will not:
- predict whether an aircraft will fail
- claim that report counts represent true aircraft failure rates
- include every field in the FAA dataset
- build a large or complex machine learning system

## Success Criteria
The MVP is successful if:
- the raw FAA dataset can be processed reproducibly
- users can filter and explore maintenance reports through the application
- the main dashboard works without manually editing the data
- the project has basic automated tests
- the project is documented well enough that another person can understand how it works

## Known Limitations
- the FAA dataset contains a large amount of missing data in some fields
- report counts do not account for fleet size, flight hours, or number of aircraft in service
- aircraft model names may require normalization
- some coded fields such as JASCCode still need to be investigated
- the initial version will probably only use a limited number of years