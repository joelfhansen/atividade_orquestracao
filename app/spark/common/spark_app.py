import os
import logging
import os
from pyspark.sql import SparkSession
import argparse

class SparkApp:

    

    def __init__(self, name):
        self._logging = logging.getLogger(__name__)
        self._logging.setLevel(logging.INFO)

        self._RAW_DIR = '/opt/airflow/data/raw'
        self._PROCESSING_DIR = '/opt/airflow/data/processing'
        self._PROCESSED_DIR = '/opt/airflow/data/processed'

        self._LISTING_FILE = os.path.join(self._RAW_DIR, 'listing_scrape.json')
        self._AVAILABILITY_FILE = os.path.join(self._RAW_DIR, 'listing_availability_scrape.json')

        self._LISTING_PARQUET = os.path.join(self._PROCESSING_DIR, 'listing.parquet')
        self._AVAILABILITY_PARQUET = os.path.join(self._PROCESSING_DIR, 'availability.parquet')
        self._FINAL_DF_PARQUET = os.path.join(self._PROCESSING_DIR, 'final_df.parquet')

        self._FINAL_TABLE = os.path.join(self._PROCESSED_DIR, 'final_table.parquet')

        parser = argparse.ArgumentParser()
        parser.add_argument('--transform_type', type=str, default='LAKE_READY')
        parser.add_argument('--debug', action='store_true')
        self._args = parser.parse_args()

        self._spark = SparkSession.builder.appName(name).getOrCreate()


    def __del__(self):
        try:
            if hasattr(self, '_spark'):
                self._spark.stop()
                self._logging.info("Spark session stopped.")
        except Exception as e:
            self._logging.error(f"Spark session not found for stop: {e}")
