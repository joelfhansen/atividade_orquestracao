from common.spark_app import SparkApp
  
class Transform(SparkApp):

    def __init__(self):
        super().__init__("02_transform_data")

    def run(self):
        listing = self._spark.read.parquet(self._LISTING_PARQUET)
        availability = self._spark.read.parquet(self._AVAILABILITY_PARQUET)

        merged_df = listing.join(availability, listing.listing_id_str == availability.airbnb_id, "inner")

        if self._args.debug:
            print(f"Merged count: {merged_df.count()}")
            merged_df.printSchema()

        if self._args.transform_type == "LAKE_READY":
            details_cols = [c for c in merged_df.columns if c not in ['id', 'listing_id_str', 'airbnb_id', 'listing_dates']]
            details_struct = struct(*[col(c) for c in details_cols])
            final_df = merged_df.select(
                col('airbnb_id'),
                details_struct.alias('details'),
                col('listing_dates').alias('availability_dates')
            )
        elif self._args.transform_type == "ANALYSIS_READY":
            exploded_df = merged_df.withColumn('listing_dates', explode('listing_dates'))
            from pyspark.sql.functions import col, struct, to_json
            # Normaliza os objetos da coluna listing_dates
            # Supondo que listing_dates é um array de structs/dicts
            # Se for string, pode ser necessário ajustar
            listing_dates_cols = exploded_df.select('listing_dates.*').columns
            final_df = exploded_df
            for c in listing_dates_cols:
                final_df = final_df.withColumn(c, col('listing_dates')[c])
            details_cols = [c for c in exploded_df.columns if c not in ['id', 'listing_id_str', 'airbnb_id', 'listing_dates']]
            details_struct = struct(*[col(c) for c in details_cols])
            final_df = final_df.select(
                col('airbnb_id'),
                *[col(c) for c in listing_dates_cols],
                details_struct.alias('details')
            )
        else:
            raise ValueError(f"transform_type inválido: {self._args.transform_type}")

        if self._args.debug:
            print(f"Final df count: {final_df.count()}")
            final_df.printSchema()

        final_df.write.mode("overwrite").parquet(self._FINAL_DF_PARQUET)

if __name__ == "__main__":
    app = Transform()
    app.run()
