from app.core.database import SessionLocal
from app.ingestion.csv_source import CSVExtractor
from app.ingestion.api_source import CoinPaprikaExtractor, CoinGeckoExtractor
from app.ingestion.rss_source import RSSExtractor
import uuid
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_etl():
    db = SessionLocal()
    batch_run_id = str(uuid.uuid4())
    try:
        # 1. CSV Extraction
        logger.info(f"Starting CSV Ingestion (Run: {batch_run_id})...")
        csv_path = os.path.join("data", "products.csv")
        csv_extractor = CSVExtractor(db, csv_path, run_id=batch_run_id)
        csv_extractor.run()
        logger.info("CSV Ingestion completed.")

        # 2. CoinPaprika Extraction
        logger.info(f"Starting CoinPaprika Ingestion (Run: {batch_run_id})...")
        cp_extractor = CoinPaprikaExtractor(db, run_id=batch_run_id)
        cp_extractor.run()
        logger.info("CoinPaprika Ingestion completed.")

        # 3. CoinGecko Extraction
        logger.info(f"Starting CoinGecko Ingestion (Run: {batch_run_id})...")
        cg_extractor = CoinGeckoExtractor(db, run_id=batch_run_id)
        cg_extractor.run()
        logger.info("CoinGecko Ingestion completed.")

        # 4. RSS Extraction
        logger.info(f"Starting RSS Ingestion (Run: {batch_run_id})...")
        rss_url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
        rss_extractor = RSSExtractor(db, rss_url, run_id=batch_run_id)
        rss_extractor.run()
        logger.info("RSS Ingestion completed.")

    except Exception as e:
        logger.error(f"ETL failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_etl()
