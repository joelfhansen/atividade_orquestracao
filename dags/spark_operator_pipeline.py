from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime

default_args = {
    'start_date': datetime(2025, 1, 1),
    'retries': 0,
}

with DAG('spark_operator_pipeline',
         default_args=default_args,
         tags=['exemplo', 'spark', 'operator-execution'],
         schedule=None,
         catchup=False
) as dag:

    spark_task = SparkSubmitOperator(
        task_id='submit_spark_job',
        application='/opt/airflow/app/spark/job_exemplo.py',
        conn_id='spark_default',
        #verbose=True,
        name='ExemploSparkJob',
        conf={
            'spark.master': 'spark://spark-master:7077',
            'spark.eventLog.enabled': 'true',
            'spark.eventLog.dir': '/opt/airflow/spark-events'
        },
        application_args=[],
    )
