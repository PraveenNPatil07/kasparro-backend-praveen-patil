# Frontend Assets (`app/static/`)

This directory contains the files for the web-based dashboard.

## Files

- **`index.html`**: A single-page application built with **Tailwind CSS** and **Alpine.js**.
    - **Dashboard**: Displays real-time health and ETL statistics.
    - **Data Explorer**: Allows searching and filtering unified records.
    - **Actions**: Buttons to manually trigger ETL jobs and upload CSV files.
    - **Grouping**: Automatically groups records by source (10 per source) on the home page.

## Usage

The `app/main.py` file mounts this directory to the `/static` path and serves `index.html` at the root URL (`/`).
