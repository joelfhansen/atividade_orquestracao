import os
import re
import json
import json5
import logging
import pandas as pd
from datetime import datetime
from pandas.io.common import StringIO

class AirbnbDataPipelinePandas:

    __RAW_DIR = 'data/raw'
    __PROCESSING_DIR = 'data/processing'
    __PROCESSED_DIR = 'data/processed'
    __LISTING_FILE = os.path.join(__RAW_DIR, 'listing_scrape.json')
    __AVAILABILITY_FILE = os.path.join(__RAW_DIR, 'listing_availability_scrape.json')
    __FINAL_TABLE = os.path.join(__PROCESSED_DIR, 'final_table.parquet')
    __XCOM_MODES = ["CONTENT", "FILEPATH"]

    def __init__(self):
        # Configurar o logger
        self.__logging = logging.getLogger(__name__)
        self.__logging.setLevel(logging.INFO)
        
        # Verificar se os diretórios e arquivos necessários existem
        if not os.path.exists(self.__RAW_DIR):
            msg = f"Diretório de dados brutos {self.__RAW_DIR} não existe."
            self.__logging.error(msg)
            raise FileNotFoundError(msg)
        if not os.path.exists(self.__LISTING_FILE) or not os.path.exists(self.__AVAILABILITY_FILE):
            msg = "Arquivos JSON necessários não encontrados."
            self.__logging.error(msg)
            raise FileNotFoundError(msg)

        if not os.path.exists(self.__PROCESSING_DIR):
            os.makedirs(self.__PROCESSING_DIR)

        if not os.path.exists(self.__PROCESSED_DIR):
            os.makedirs(self.__PROCESSED_DIR)


    def getXComModes(self):
        return self.__XCOM_MODES


    def __load_sanitized_json_file_as_df(self, filepath):
        try:
            # 1 tentativa: ler com json5
            with open(filepath, 'r', encoding='utf-8') as f:
                content_json = json5.load(f)
            return pd.json_normalize(content_json)
        except Exception as e_json5:
            logging.warning(f"Falha ao ler {filepath} com json5: {e_json5}. Tentando sanitizar...")
            try:
                # 2 tentativa: ler com pandas
                return pd.read_json(filepath)
            except ValueError as e:
                # 3 tentativa: sanitizar manualmente
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    # Remove comentários (// ou #)
                    content = re.sub(r'//.*|#.*', '', content)
                    # Corrige aspas simples para duplas
                    content = re.sub(r"'", '"', content)
                    # Remove vírgulas finais antes de fechar objetos/arrays
                    content = re.sub(r',([\s\n]*[}\]])', r'\1', content)
                    # Tenta carregar para validar
                    json.loads(content)
                    return pd.read_json(StringIO(content))
                except Exception as e:
                    logging.error(f"Não foi possível sanitizar o JSON {filepath}: {e}")
                    raise
                    

    def __show_file_content(self, df):
        df_columns = df.columns.tolist()
        df_head = df.head().to_dict(orient='records')
        self.__logging.info(f"Colunas do DataFrame: {df_columns}")
        self.__logging.info(f"Primeiras linhas do DataFrame: {df_head}")

        # printar os dados de cada coluna no formato Nome: Valor
        # para cada registro no df
        for index, row in df.iterrows():
            self.__logging.info(f"================= Registro {str(index+1).zfill(5)} ======================")
            for col in df_columns:
                self.__logging.info(f"{col}: {row[col]}")  # Mostra o valor de cada coluna para o registro atual
        self.__logging.info(f"=======================================================")


    def ingest_data(self, **kwargs):
        try:
            ##### 1 - Carregar Estado #####

            # mostrar o diretorio corrente
            self.__logging.info(f"Diretório de trabalho atual: {os.getcwd()}")
            self.__logging.info(f"Caminho do arquivo de listing: {self.__LISTING_FILE}")
            self.__logging.info(f"Caminho do arquivo de availability: {self.__AVAILABILITY_FILE}")
            

            ##### 2 - Processar #####

            self.__logging.info("Iniciando a ingestão dos dados.")

            self.__logging.info(f"Carregando arquivo {self.__LISTING_FILE}...")
            listing = self.__load_sanitized_json_file_as_df(self.__LISTING_FILE)
            self.__logging.info(f"DataFrame de listing carregado com {len(listing)} registros.")

            self.__logging.info(f"Carregando arquivo {self.__AVAILABILITY_FILE}...")
            availability = self.__load_sanitized_json_file_as_df(self.__AVAILABILITY_FILE)
            self.__logging.info(f"DataFrame de availability carregado com {len(availability)} registros.")

            if listing.empty or availability.empty:
                msg = "Os DataFrames de listing ou availability estão vazios após a leitura dos arquivos JSON."
                self.__logging.error(msg)
                raise ValueError(msg)

            self.__show_file_content(listing)
            self.__show_file_content(availability)
            
            ##### 3 - Armazenar o estado #####
            
            xcom_mode = kwargs.get('params', {}).get('xcom_mode')
            if xcom_mode not in self.__XCOM_MODES:
                msg = f"Modo de comunicação inválido: {xcom_mode}. Deve ser um dos: {self.__XCOM_MODES}."
                self.__logging.error(msg)
                raise ValueError(msg)
            
            if xcom_mode == "FILEPATH":
                # Salvar os DataFrames como arquivos Parquet
                listing_file_path = os.path.join(self.__PROCESSING_DIR, 'listing.parquet')
                availability_file_path = os.path.join(self.__PROCESSING_DIR, 'availability.parquet')

                self.__logging.info(f"Salvando DataFrame de listing em {listing_file_path}")
                self.__logging.info(f"Salvando DataFrame de availability em {availability_file_path}")

                listing.to_parquet(listing_file_path, index=False)
                availability.to_parquet(availability_file_path, index=False)

                # Armazenar os caminhos dos DataFrames no XCom
                kwargs['ti'].xcom_push(key='listing_file_path', value=listing_file_path)
                kwargs['ti'].xcom_push(key='availability_file_path', value=availability_file_path)
            else:
                # Armazenar os DataFrames no XCom como JSON
                kwargs['ti'].xcom_push(key='listing_content', value=listing.to_json())
                kwargs['ti'].xcom_push(key='availability_content', value=availability.to_json())

            self.__logging.info("Ingestão realizada com sucesso.")
        except Exception as e:
            self.__logging.error(f"Erro na etapa de ingestão: {e}")
            raise


    def transform_data(self, **kwargs):
        try:
            ##### 1 - Carregar Estado #####
            xcom_mode = kwargs.get('params', {}).get('xcom_mode')
            if xcom_mode not in self.__XCOM_MODES:
                msg = f"Modo de comunicação inválido: {xcom_mode}. Deve ser um dos: {self.__XCOM_MODES}."
                self.__logging.error(msg)
                raise ValueError(msg)

            if xcom_mode == "CONTENT":
                # Carregar os DataFrames do XCom
                listing_content = kwargs['ti'].xcom_pull(key='listing_content', task_ids='ingest_data')
                availability_content = kwargs['ti'].xcom_pull(key='availability_content', task_ids='ingest_data')
                # Valida se os dados foram encontrados
                if listing_content is None or availability_content is None:
                    msg = "Dados não encontrados no XCom: listing_content ou availability_content."
                    self.__logging.error(msg)
                    raise ValueError(msg)
                # Carrega o conteúdo dos Jsons
                self.__logging.info("Carregando DataFrames a partir do conteúdo JSON...")
                listing = pd.read_json(StringIO(listing_content))
                availability = pd.read_json(StringIO(availability_content))
            else:
                # Carregar os caminhos dos DataFrames do XCom
                listing_file_path = kwargs['ti'].xcom_pull(key='listing_file_path', task_ids='ingest_data')
                availability_file_path = kwargs['ti'].xcom_pull(key='availability_file_path', task_ids='ingest_data')
                # Valida se os caminhos foram encontrados
                if listing_file_path is None or availability_file_path is None:
                    msg = "Dados não encontrados no XCom: listing_file_path ou availability_file_path."
                    self.__logging.error(msg)
                    raise ValueError(msg)
                # Carrega o conteúdo dos arquivos Parquet
                self.__logging.info("Carregando DataFrames a partir dos arquivos Parquet...")
                listing = pd.read_parquet(listing_file_path)
                availability = pd.read_parquet(availability_file_path)

            self.__logging.info(f"DataFrame de listing carregado com {len(listing)} registros.")
            self.__logging.info(f"DataFrame de availability carregado com {len(availability)} registros.")

            self.__logging.info(f"listing.dtypes:\n{listing.dtypes}")
            self.__logging.info(f"availability.dtypes:\n{availability.dtypes}")

            ##### 2 - Processar #####

            self.__logging.info("Iniciando merge dos DataFrames...")
            # Faz o merge dos DataFrames
            merged_df = pd.merge(listing, availability, left_on='listing_id_str', right_on='airbnb_id', how='inner')
            self.__logging.info(f"Merge realizado com sucesso. Dataframe com {len(merged_df)} registros.")

            self.__logging.info("Iniciando a transformação dos dados...")
            # 1 - separar as colunas dos detalhes do listing
            listing_df = merged_df.drop(columns=['id', 'listing_id_str', 'airbnb_id', 'listing_dates'])
            
            # 2 - Colocar a coluna airbnb_id em primeiro
            final_df = merged_df['airbnb_id'].to_frame()
            
            # 3 - Colocar todas as colunas do listing como subcoluna de uma coluna 'details'
            final_df['details'] = listing_df.to_dict(orient='records')
            
            # 4 - Adicionar 'listing_dates' como nome 'availability_dates'
            final_df['availability_dates'] = merged_df['listing_dates']
            final_df = final_df[['airbnb_id', 'details', 'availability_dates']]
            
            # Exibir o conteúdo do DataFrame final
            self.__logging.info("DataFrame final após transformação:")
            self.__logging.info(f"final_df.dtypes:\n{final_df.dtypes}")
            self.__logging.info(f"final_df.shape: {final_df.shape}")
            
            ##### 3 - Armazenar o estado #####

            if xcom_mode == "CONTENT":
                # Armazenar o DataFrame final no XCom como JSON
                self.__logging.info("Armazenando DataFrame final no XCom como JSON.")
                kwargs['ti'].xcom_push(key='final_df_content', value=final_df.to_json())
            else:
                # Salvar o DataFrame final como arquivo Parquet
                final_df_file_path = os.path.join(self.__PROCESSING_DIR, 'final_df.parquet')
                self.__logging.info(f"Salvando DataFrame final em {final_df_file_path}")
                final_df.to_parquet(final_df_file_path, index=False)
                kwargs['ti'].xcom_push(key='final_df_filepath', value=final_df_file_path)

            self.__logging.info("Transformação realizada com sucesso.")
        except Exception as e:
            self.__logging.error(f"Erro na etapa de transformação: {e}")
            raise


    def save_final_table(self, **kwargs):
        try:
            ##### 1 - Carregar o Estado #####
            xcom_mode = kwargs.get('params', {}).get('xcom_mode')
            if xcom_mode not in self.__XCOM_MODES:
                msg = f"Modo de comunicação inválido: {xcom_mode}. Deve ser um dos: {self.__XCOM_MODES}."
                self.__logging.error(msg)
                raise ValueError(msg)
                
            if xcom_mode == "CONTENT":
                final_df_content = kwargs['ti'].xcom_pull(key='final_df_content', task_ids='transform_data')
                if final_df_content is None:
                    msg = "Dados final_df não encontrados no XCom."
                    self.__logging.error(msg)
                    raise ValueError(msg)
                final_df = pd.read_json(StringIO(final_df_content))
            else:
                final_df_filepath = kwargs['ti'].xcom_pull(key='final_df_filepath', task_ids='transform_data')
                if final_df_filepath is None:
                    msg = "Caminho do DataFrame final não encontrado no XCom."
                    self.__logging.error(msg)
                    raise ValueError(msg)
                final_df = pd.read_parquet(final_df_filepath)
            
            self.__show_file_content(final_df)

            ##### 2 - Processar #####

            self.__logging.info("Iniciando o salvamento da tabela final.")
            
            final_df.to_parquet(self.__FINAL_TABLE, index=False)
            
            self.__logging.info("Tabela final salva com sucesso.")
            
            ##### 3 - Armazenar o estado #####

            kwargs['ti'].xcom_push(key='final_df_filepath', value=self.__FINAL_TABLE)
        except Exception as e:
            self.__logging.error(f"Erro na etapa de salvamento da tabela final: {e}")
            raise