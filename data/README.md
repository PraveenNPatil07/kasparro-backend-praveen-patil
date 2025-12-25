# Data Sources (`data/`)

This directory stores the local files used as input for the ETL pipeline.

## Files

- **`products.csv`**: The primary source file for the `CSVExtractor`. It contains product information (id, title, price, etc.) that is ingested into the system.

## Notes

In a production environment, this directory is often mounted as a volume to allow for persistent storage of uploaded or generated files.
