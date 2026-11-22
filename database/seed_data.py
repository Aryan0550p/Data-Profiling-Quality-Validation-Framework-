"""
Database loader and SQL test runner.
Loads the 8 enterprise datasets into SQLite or PostgreSQL via SQLAlchemy,
and provides functionality to execute SQL data quality audits.
"""

import logging
import sqlite3
import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text

from src.config import (
    DATABASE_DIR,
    RAW_DATA_DIR,
    CLEAN_DATA_DIR,
    DATASETS_SCHEMA,
    SQLITE_DB_PATH,
    SQLITE_URL
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class DatabaseLoader:
    def __init__(self, db_url: str = SQLITE_URL):
        self.db_url = db_url
        self.engine = create_engine(self.db_url)

    def load_all_datasets(self, source_dir: Path = RAW_DATA_DIR, table_prefix: str = ""):
        """Loads all 8 tables into the SQL database."""
        logger.info(f"Connecting to database at {self.db_url}...")
        for name in DATASETS_SCHEMA.keys():
            csv_path = source_dir / f"{name}.csv"
            if not csv_path.exists():
                logger.warning(f"File {csv_path} does not exist.")
                continue

            df = pd.read_csv(csv_path)
            target_table = f"{table_prefix}{name}"
            df.to_sql(target_table, con=self.engine, if_exists="replace", index=False)
            logger.info(f"Loaded {len(df):,} rows into table: {target_table}")

    def run_sql_quality_audits(self) -> pd.DataFrame:
        """Runs the standalone SQL data quality test suite."""
        sql_file = DATABASE_DIR / "sql_quality_checks.sql"
        if not sql_file.exists():
            raise FileNotFoundError(f"{sql_file} not found.")

        with open(sql_file, "r") as f:
            content = f.read()

        # Split into individual queries separated by semicolon
        raw_queries = [q.strip() for q in content.split(";") if q.strip()]
        results = []

        with self.engine.connect() as conn:
            for q in raw_queries:
                # Skip comments-only blocks
                lines = [l for l in q.split("\n") if not l.strip().startswith("--")]
                clean_q = "\n".join(lines).strip()
                if not clean_q or not clean_q.upper().startswith("SELECT"):
                    continue

                try:
                    res = conn.execute(text(clean_q))
                    rows = res.fetchall()
                    for r in rows:
                        results.append(dict(r._mapping))
                except Exception as e:
                    logger.warning(f"Query audit failed on query:\n{clean_q[:60]}...\nError: {e}")

        df_results = pd.DataFrame(results)
        return df_results


if __name__ == "__main__":
    loader = DatabaseLoader()
    # Load raw data as standard tables
    loader.load_all_datasets(source_dir=RAW_DATA_DIR, table_prefix="")
    # Load cleaned data with prefix clean_
    loader.load_all_datasets(source_dir=CLEAN_DATA_DIR, table_prefix="clean_")

    print("\n--- RUNNING STANDALONE SQL DATA QUALITY AUDIT SUITE ---")
    audit_results = loader.run_sql_quality_audits()
    if not audit_results.empty:
        print(audit_results.to_string(index=False))
    else:
        print("Audit suite executed.")
