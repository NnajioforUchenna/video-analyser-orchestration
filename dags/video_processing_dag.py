import logging
from datetime import datetime, timedelta

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
from airflow.decorators import task
from airflow.models import Variable
# Operators; we need this to operate!
from airflow.utils.trigger_rule import TriggerRule

from check_video_status import getCurrentVideoToProcessed, setCurrentVideoToProcessed
from download_video_from_drive import download_video_from_drive
from getNewSessions import getNewSessions
from video_audio_spliting import split_video_into_chunks

with DAG(
        "video_processing_DAG",
        default_args={
            "depends_on_past": False,
            "email": ["code2stories@gmail.com"],
            "email_on_failure": False,
            "email_on_retry": False,
            "retries": 1,
            "retry_delay": timedelta(minutes=5),
        },
        description="Video Processing For VAN",
        schedule_interval=timedelta(days=1),
        start_date=datetime(2024, 5, 19),
        catchup=False,
        tags=["example"],
) as dag:
    # t1, t2 and t3 are examples of tasks created by instantiating operators
    @task()
    def getNewVideoSessions():
        logging.info('Getting New Sessions I was called to run')
        new_sessions = getNewSessions()
        return new_sessions


    @task.branch()
    def checkNewSessions():
        newSession = setCurrentVideoToProcessed()
        if newSession:
            return 'download_video'
        else:
            return 'no_new_sessions'


    @task(task_id='download_video')
    def download_video():
        newSession = getCurrentVideoToProcessed()
        filePath = download_video_from_drive(newSession)
        logging.info('Downloading Video')
        Variable.set('video_file_path', filePath)
        return filePath


    @task(task_id='no_new_sessions')
    def no_new_sessions():
        logging.info('No new sessions to process')
        return 'No new sessions to process'


    @task(trigger_rule=TriggerRule.ALL_DONE)
    def split_video_task():
        logging.info('Triggering Celery task to split video')
        filePath = Variable.get('video_file_path')
        print(filePath)
        split_video_into_chunks.apply_async(args=[filePath])
        return "Video split task triggered successfully"


    getNewVideoSessions() >> checkNewSessions() >> [download_video(), no_new_sessions()] >> split_video_task()
