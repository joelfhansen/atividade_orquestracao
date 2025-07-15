from airflow import DAG
from airflow.providers.ssh.operators.ssh import SSHOperator
from datetime import datetime

default_args = {
    'start_date': datetime(2025, 1, 1),
    'retries': 0,
}

with DAG('spark_pipeline_ssh',
         default_args=default_args,
         tags=['exemplo', 'spark', 'ssh-execution'],
         schedule=None,
         catchup=False
) as dag:

    spark_ssh_task = SSHOperator(
        task_id='submit_spark_job_ssh',
        ssh_conn_id='spark_master_ssh',  # Defina essa conexão no Airflow
        command='export JAVA_HOME=/opt/java/openjdk && /opt/spark/bin/spark-submit --master spark://spark-master:7077 /opt/airflow/app/spark/job_exemplo.py',
        do_xcom_push=True,
        cmd_timeout=600
        
    )