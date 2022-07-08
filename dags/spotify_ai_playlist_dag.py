
import datetime as dt
from datetime import timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from helper_functions.spotify_add_playlist import create_spotify_playlist

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': dt.datetime(2022, 6, 25),
    'email': ['dag-failure@thaller.dev'], # emails me if there's a dag failure
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

dag = DAG(
    dag_id='spotify_playlist_dag',
    tags=['Spotify'],
    default_args=default_args,
    description='Spotify DAG Playlist',
    schedule_interval=timedelta(days=7)
)



# operators determine what gets done by a task. one operator = one dtask.
# lots of operators like bash operator, sql operator, python operator
# XCom for passing info from one operator to another type of operator. generally bad practice, but possible

# def just_a_function():
#     print('Test Function Run Successful')

run_etl = PythonOperator(
    task_id='spotify_playlist_dag',
    python_callable=create_spotify_playlist,
    dag=dag
)

run_etl
# ex t1 >> [t2, t3]


# https://www.datasciencelearner.com/importerror-attempted-relative-import-parent-package/
#  TODO: comeback to add these to be global packages instead.