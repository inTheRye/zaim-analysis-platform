from airflow import DAG
from airflow.operators import BashOperator
from datetime import datetime

default_args = {
    'owner': 'root',
    'start_date': datetime.today(),
}

dag = DAG('zaim', default_args=default_args, schedule_interval='00 00 * * *')

task1 = BashOperator(
    task_id='retrieve_zaim_data',
    bash_command='python /app/zaim_downloader.py',
    dag=dag)

task2 = BashOperator(
    task_id='update_data',
    bash_command='/app/update_data.sh ',
    dag=dag)

task1.set_downstream(task2)
