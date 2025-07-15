#!/bin/bash
airflow connections delete 'spark_default' || true
airflow connections add 'spark_default' \
    --conn-type 'spark' \
    --conn-host 'spark://spark-master' \
    --conn-port '7077' \
    --conn-extra '{"deploy_mode": "cluster", "spark_binary": "spark-submit"}'

airflow connections delete 'spark_master_ssh' || true
airflow connections add 'spark_master_ssh' \
    --conn-type 'ssh' \
    --conn-host 'spark-master' \
    --conn-port '22' \
    --conn-login 'spark' \
    --conn-extra '{"key_file": "/opt/airflow/ssh/id_rsa"}'
