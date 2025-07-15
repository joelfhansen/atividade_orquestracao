from pyspark.sql import SparkSession
import random

spark = SparkSession.builder.appName("PiEstimation").getOrCreate()

NUM_SAMPLES = 1000000

def inside(p):
    x, y = random.random(), random.random()
    return x**2 + y**2 <= 1

rdd = spark.sparkContext.parallelize(range(NUM_SAMPLES))
count = rdd.filter(inside).count()

pi_estimate = 4.0 * count / NUM_SAMPLES
print(f"Estimated value of Pi is: {pi_estimate}")

spark.stop()