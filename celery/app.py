import time
from datetime import datetime

from celery import Celery
import tasks


celery = Celery(
    __name__,
    backend='redis://127.0.0.1:6379/3',
    broker='redis://127.0.0.1:6379/4',
    include=tasks.__name__,
)


@celery.task
def task2():
    print('celery task')
    time.sleep(2)
    now = datetime.now()
    print(now)
    return now
