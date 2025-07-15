from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime

default_args = {
    'start_date': datetime(2025, 1, 1),
    'retries': 1,
}

with DAG('teste_operator_spark_pipeline_dag',
         default_args=default_args,
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
            # 'spark.eventLog.enabled': 'true',
            # 'spark.eventLog.dir': '/tmp/spark-events'
        },
        application_args=[],
    )
