import os
import logging
import pandas as pd
from datetime import datetime

RAW_DIR = 'data/raw'
PROCESSED_DIR = 'data/processed'
LISTING_FILE = os.path.join(RAW_DIR, 'listing_scrape.json')
AVAILABILITY_FILE = os.path.join(RAW_DIR, 'listing_availability_scrape.json')
FINAL_TABLE = os.path.join(PROCESSED_DIR, 'final_table.parquet')


def ingest_data(**kwargs):
    try:
        # mostrar o diretorio corrente
        logging.info(f"Current working directory: {os.getcwd()}")
        # mostrr o caminho dos arquivos
        logging.info(f"Caminho do arquivo de listing: {LISTING_FILE}")
        logging.info(f"Caminho do arquivo de availability: {AVAILABILITY_FILE}")
        if not os.path.exists(RAW_DIR):
            raise FileNotFoundError(f"Raw data directory {RAW_DIR} does not exist.")
        if not os.path.exists(LISTING_FILE) or not os.path.exists(AVAILABILITY_FILE):
            raise FileNotFoundError("Required JSON files are missing.")
        
        logging.info("Iniciando a ingestão dos dados.")
        listing = pd.read_json(LISTING_FILE)
        availability = pd.read_json(AVAILABILITY_FILE)
        kwargs['ti'].xcom_push(key='listing', value=listing.to_json())
        kwargs['ti'].xcom_push(key='availability', value=availability.to_json())
        logging.info("Ingestão realizada com sucesso.")
    except Exception as e:
        logging.error(f"Erro na ingestão: {e}")
        raise


def transform_data(**kwargs):
    try:
        listing = pd.read_json(kwargs['ti'].xcom_pull(key='listing'))
        availability = pd.read_json(kwargs['ti'].xcom_pull(key='availability'))
        final_df = pd.merge(listing, availability, on='id', how='inner')
        kwargs['ti'].xcom_push(key='final_df', value=final_df.to_json())
        logging.info("Transformação realizada com sucesso.")
    except Exception as e:
        logging.error(f"Erro na transformação: {e}")
        raise


def save_final_table(**kwargs):
    try:
        if not os.path.exists(PROCESSED_DIR):
            os.makedirs(PROCESSED_DIR)
        final_df = pd.read_json(kwargs['ti'].xcom_pull(key='final_df'))
        final_df.to_parquet(FINAL_TABLE, index=False)
        logging.info("Tabela final salva com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao salvar tabela final: {e}")
        raise