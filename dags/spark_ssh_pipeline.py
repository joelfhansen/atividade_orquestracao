from airflow import DAG
from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.models import Param
from datetime import datetime

default_args = {
    'start_date': datetime(2025, 1, 1),
    'retries': 0,
}

with DAG(
    dag_id='spark_ssh_pipeline',
    default_args=default_args,
    schedule=None,
    catchup=False,
    tags=['airbnb-data', 'spark', 'ssh-execution'],
    params={
        'transform_type': Param('LAKE_READY', type='string', enum=['LAKE_READY', 'ANALYSIS_READY']),
        'debug': Param(False, type='boolean'),
    }
) as dag:

    ingest = SSHOperator(
        task_id='spark_ingest_data',
        ssh_conn_id='spark_master_ssh',
        cmd_timeout=600,
        command="export JAVA_HOME=/opt/java/openjdk && \
                 /opt/spark/bin/spark-submit \
                 --master spark://spark-master:7077 \
                 --conf spark.eventLog.enabled=true \
                 --conf spark.eventLog.dir=/opt/spark-events \
                 /opt/airflow/app/spark/01_ingest_data.py --transform_type {{ params.transform_type }} {% if params.debug %} --debug {% endif %}",
    )

    # transform = SSHOperator(
    #     task_id='spark_transform_data',
    #     ssh_conn_id='spark_master_ssh',
    #     cmd_timeout=600,
    #     command="export JAVA_HOME=/opt/java/openjdk && \
    #              /opt/spark/bin/spark-submit \
    #              --master spark://spark-master:7077 \
    #              --conf spark.eventLog.enabled=true \
    #              --conf spark.eventLog.dir=/opt/spark-events \
    #              /opt/airflow/app/spark/02_transform_data.py --transform_type {{ params.transform_type }} {% if params.debug %} --debug {% endif %}",
    # )

    # save = SSHOperator(
    #     task_id='spark_save_final_table',
    #     ssh_conn_id='spark_master_ssh',
    #     cmd_timeout=600,
    #     command="export JAVA_HOME=/opt/java/openjdk && \
    #              /opt/spark/bin/spark-submit \
    #              --master spark://spark-master:7077 \
    #              --conf spark.eventLog.enabled=true \
    #              --conf spark.eventLog.dir=/opt/spark-events \
    #              /opt/airflow/app/spark/03_save_final_table.py --transform_type {{ params.transform_type }} {% if params.debug %} --debug {% endif %}",
    # )

    ingest #>> transform >> save