# Dataset Metadata

## Title

Wetter seit 1872 – Hohe Warte Wien

## Description

This dataset contains historical monthly weather observations recorded at the Hohe Warte meteorological station in Vienna, Austria. The dataset includes measurements such as temperature, precipitation, pressure, humidity, and wind.

## Original Publisher

Stadt Wien (City of Vienna), Municipal Department 23 (MA 23)

## Source

https://www.data.gv.at/datasets/69a06550-1ede-4f50-9c36-e7fb5cf6e7e8

## License

Creative Commons Attribution 4.0 (CC BY 4.0)

## Rights Holder

Stadt Wien

## Contribution (This Project)

The dataset was re-published, cleaned, and transformed into a relational database schema (3NF) as part of a university assignment. No ownership of the original data is claimed.

## Data Structure
The dataset is organized into three relational tables:

- station: static metadata about the weather station
- time_dimension: temporal information (year, month)
- weather_measurement: monthly weather observations linked to station and time

## Notes

This work only restructures and stores the data in DBRepo for analysis purposes.
