from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("ExemploJob").getOrCreate()

data = [("Alice", 34), ("Bob", 45), ("Cathy", 29)]
df = spark.createDataFrame(data, ["Nome", "Idade"])
df.show()

spark.stop()
