import sys, os
from datetime import datetime
from airflow import DAG
from airflow.models import Param
from airflow.operators.python import PythonOperator

sys.path.append('/opt/airflow/app')
from local.airbnb_pandas import AirbnbDataPipelinePandas


pipeline = AirbnbDataPipelinePandas()

def ingest(**kwargs):
    return pipeline.ingest_data(**kwargs)

def transform(**kwargs):
    return pipeline.transform_data(**kwargs)

def save(**kwargs):
    return pipeline.save_final_table(**kwargs)


default_args = {
    'start_date': datetime(2023, 1, 1),
    'retries': 0,
}


with DAG(
    dag_id='pandas_pipeline',
    default_args=default_args,
    schedule=None,
    catchup=False,
    tags=['airbnb-data', 'pandas', 'airflow-execution'],
    params={
        "xcom_mode": Param(
            pipeline.getXComModes()[0],
            type="string",
            enum=pipeline.getXComModes(),
            title="Modo de comunicação entre as tarefas",
        ),

    }
) as dag:

    ingest = PythonOperator(
        task_id='ingest_data',
        python_callable=ingest,
    )

    transform = PythonOperator(
        task_id='transform_data',
        python_callable=transform,
    )

    save = PythonOperator(
        task_id='save_final_table',
        python_callable=save,
    )

    ingest >> transform >> save
