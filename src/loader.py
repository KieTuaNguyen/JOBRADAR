
import logging
import os
from pathlib import Path

import pandas as pd
import snowflake.connector
from dotenv import load_dotenv
from snowflake.connector.pandas_tools import write_pandas

load_dotenv()

RAW_DIR    = Path(__file__).resolve().parents[1] / "data" / "raw"
TABLE_NAME = "JOB_LISTINGS"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

def get_latest_csv(directory: Path) -> Path:
    """Return the most recently created CSV in data/raw/."""
    csvs = sorted(directory.glob("jora_raw_*.csv"), reverse=True)
    if not csvs:
        raise FileNotFoundError(f"No raw CSV files found in {directory}")
    latest = csvs[0]
    log.info("Latest CSV: %s", latest.name)
    return latest


def get_connection() -> snowflake.connector.SnowflakeConnection:
    conn = snowflake.connector.connect(
        account   = os.environ["SNOWFLAKE_ACCOUNT"],
        user      = os.environ["SNOWFLAKE_USER"],
        password  = os.environ["SNOWFLAKE_PASSWORD"],
        warehouse = os.environ["SNOWFLAKE_WAREHOUSE"],
        database  = os.environ["SNOWFLAKE_DATABASE"],
        schema    = os.environ["SNOWFLAKE_SCHEMA"],
        role      = os.environ["SNOWFLAKE_ROLE"],
    )
    log.info("Connected to Snowflake ✓")
    return conn


def prepare_dataframe(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path, encoding="utf-8-sig")

    df.columns = [c.upper() for c in df.columns]

    df["DATE_POSTED"] = pd.to_datetime(df["DATE_POSTED"], errors="coerce").dt.date
    df["SCRAPED_AT"]  = pd.to_datetime(df["SCRAPED_AT"],  errors="coerce")

    df = df.dropna(subset=["JOB_ID"])

    log.info("DataFrame ready — %d rows, %d columns", len(df), len(df.columns))
    return df


def remove_existing(conn, df: pd.DataFrame) -> None:
    job_ids = df["JOB_ID"].tolist()
    if not job_ids:
        return

    chunk_size = 1000
    cursor = conn.cursor()
    for i in range(0, len(job_ids), chunk_size):
        chunk = job_ids[i : i + chunk_size]
        placeholders = ", ".join(["%s"] * len(chunk))
        cursor.execute(
            f"DELETE FROM {TABLE_NAME} WHERE JOB_ID IN ({placeholders})",
            chunk,
        )
    cursor.close()
    log.info("Removed existing rows for %d job IDs", len(job_ids))


def load_to_snowflake(conn, df: pd.DataFrame) -> None:
    success, nchunks, nrows, _ = write_pandas(
        conn=conn,
        df=df,
        table_name=TABLE_NAME,
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=os.environ["SNOWFLAKE_SCHEMA"],
        overwrite=False,
        quote_identifiers=False,
    )
    if success:
        log.info("Loaded %d rows in %d chunk(s) ✓", nrows, nchunks)
    else:
        raise RuntimeError("write_pandas reported failure — check Snowflake logs")

def main() -> None:
    log.info("── JOBRADAR Loader starting ──")

    csv_path = get_latest_csv(RAW_DIR)

    df = prepare_dataframe(csv_path)

    conn = get_connection()

    try:
        remove_existing(conn, df)

        load_to_snowflake(conn, df)

    finally:
        conn.close()
        log.info("Connection closed.")

    log.info("── Done ──")


if __name__ == "__main__":
    main()