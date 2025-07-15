import os
import re, json
from io import StringIO
from common.spark_app import SparkApp
        
class Ingest(SparkApp):

    def __init__(self):
        super().__init__("01_ingest_data")

    def run(self):
        # Carregar os arquivos JSON
        listing = self.__load_sanitized_json_file_as_df(self._LISTING_FILE)
        availability = self.__load_sanitized_json_file_as_df(self._AVAILABILITY_FILE)

        listing = listing.cache()
        availability = availability.cache()

        if self._args.debug:
            print(f"Listing schema: {listing.printSchema()}")
            print(f"Availability schema: {availability.printSchema()}")
            print(f"Listing count: {listing.count()}")
            print(f"Availability count: {availability.count()}")

        # Salvar como Parquet para o próximo estágio
        if not os.path.exists(self._PROCESSING_DIR):
            os.makedirs(self._PROCESSING_DIR)
        listing.write.mode("overwrite").parquet(os.path.join(self._PROCESSING_DIR, "listing.parquet"))
        availability.write.mode("overwrite").parquet(os.path.join(self._PROCESSING_DIR, "availability.parquet"))


    def __load_sanitized_json_file_as_df(self, filepath):
        try:
            # 1ª tentativa: ler como JSON lines
            df = self._spark.read.json(filepath)
            if df.columns == ['_corrupt_record'] or not df.columns:
                raise ValueError("Arquivo JSON não possui colunas válidas (apenas _corrupt_record)")
            return df
        except Exception as e:
            self._logging.warning(f"Falha ao ler {filepath} como JSON lines: {e}. Tentando sanitizar...")
            # Tenta importar json5 de forma segura
            json5 = None
            try:
                import json5
            except ImportError:
                self._logging.warning("json5 não está instalado. Recomenda-se instalar para melhor compatibilidade com JSONs malformados.")
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    if json5:
                        data = json5.load(f)
                    else:
                        content = f.read()
                        # Remove comentários (// ou #)
                        content = re.sub(r'//.*|#.*', '', content)
                        content = re.sub(r"'", '"', content)
                        content = re.sub(r',([\s\n]*[}}\]])', r'\1', content)
                        # Remove caracteres de controle não permitidos, mas mantém \n e \t
                        content = re.sub(r'[\x00-\x09\x0B-\x0C\x0E-\x1F\x7F]', ' ', content)
                        data = json.loads(content)
                if isinstance(data, dict):
                    data = [data]
                if not isinstance(data, list):
                    raise ValueError("JSON não é um objeto nem uma lista de objetos.")
                df = self._spark.createDataFrame(data)
                if not df.columns:
                    raise ValueError("Arquivo JSON não possui colunas válidas após sanitização.")
                return df
            except Exception as e3:
                self._logging.error(f"Não foi possível sanitizar o JSON {filepath}: {e3}")
                raise
        

if __name__ == "__main__":
    app = Ingest()
    app.run()
