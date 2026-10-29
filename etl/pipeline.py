import logging
from pathlib import Path
from extract import extract_csv
from transform import transform_data
from validate import validate_data
from load import load_to_postgres

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "etl.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

def run():
    raw_file = Path(__file__).resolve().parent.parent / "data/raw/sales.csv"
    logger.info("ETL pipeline started.")

    raw_df = extract_csv(str(raw_file))
    logger.info("Extracted %d rows.", len(raw_df))

    # Validate the raw extract before any rows are dropped/cleaned.
    validate_data(raw_df)

    df = transform_data(raw_df)
    logger.info("Transformed %d rows.", len(df))

    # Validate the final load-ready dataset as well.
    validate_data(df)

    load_to_postgres(df)

    logger.info("Loaded %d rows into PostgreSQL.", len(df))
    logger.info("ETL pipeline completed successfully.")

if __name__ == "__main__":
    run()
