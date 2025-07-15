from common.spark_app import SparkApp
  
class Save(SparkApp):

    def __init__(self):
        super().__init__("01_ingest_data")

    def run(self):

        if not os.path.exists(self._PROCESSED_DIR):
            os.makedirs(self._PROCESSED_DIR)

        final_df = self._spark.read.parquet(self._FINAL_DF_PARQUET)
        if self._args.debug:
            print(f"Final table count: {final_df.count()}")
            final_df.printSchema()

        final_df.write.mode("overwrite").parquet(self._FINAL_TABLE)
        
if __name__ == "__main__":
    app = Save()
    app.run()
