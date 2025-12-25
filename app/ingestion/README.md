# ETL Ingestion Engine (`app/ingestion/`)

The Ingestion Engine is the most critical part of the Kasparro system. It is responsible for the full lifecycle of data: fetching it from external sources, cleaning and normalizing it, and storing it safely in the database.

## Design Patterns

### 1. The Template Method Pattern (`BaseExtractor`)
Every data source (API, CSV, RSS) follows the same logical flow defined in `BaseExtractor.run()`:
- **Pre-run**: Initialize database session and create an `ETLRun` record.
- **Extraction**: Fetch data from the source (implemented by subclasses).
- **Transformation**: Convert source-specific data into a unified `UnifiedDataCreate` schema.
- **Loading**: Perform an **UPSERT** (Update or Insert) into the `UnifiedData` table.
- **Checkpointing**: Update the `ETLCheckpoint` to mark the last successful ingestion time.
- **Post-run**: Mark the `ETLRun` as success or failure and close the session.

### 2. Idempotency & Deduplication
- **Content Hashing**: We generate a unique hash for every record based on its core fields.
- **UPSERT Logic**: If a record with the same hash already exists, we update its metadata instead of creating a duplicate. This ensures the system can be safely restarted at any time.

### 3. Incremental Ingestion
To save bandwidth and processing power, we use a **Checkpointing system**. Before fetching data, an extractor asks the database for the "Last Ingested Timestamp" for its specific source. It then only requests records newer than that timestamp.

## Source Implementations

### API Sources (`api_source.py`)
- **`CoinPaprikaExtractor`**: Connects to the CoinPaprika API. Uses pagination to fetch the latest cryptocurrency prices and market stats.
- **`CoinGeckoExtractor`**: Connects to the CoinGecko API. Implements intelligent retry logic and rate-limit handling to deal with API constraints.

### File Sources (`csv_source.py`)
- **`CSVExtractor`**: Uses **Pandas** for high-performance data processing. It handles date parsing, missing value cleanup, and schema mapping for the `products.csv` file.

### Feed Sources (`rss_source.py`)
- **`RSSExtractor`**: Uses `feedparser` to ingest news from RSS feeds. It maps fields like `published_parsed` and `summary` into the unified system.

## Orchestration (`runner.py`)

The `runner.py` script is the main entry point for the ETL service. It:
1.  Instantiates all active extractors.
2.  Executes them in a sequence (or potentially in parallel).
3.  Logs overall system performance and aggregate statistics.
