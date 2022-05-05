import time
from datetime import datetime
from celery import shared_task


@shared_task
def task3():
    print('celery shared_task')
    time.sleep(2)
    now = datetime.now()
    print(now)
    return now
