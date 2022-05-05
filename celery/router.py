from fastapi import APIRouter
from starlette.background import BackgroundTasks

from tasks import task3


router = APIRouter()


@router.get('/task4')
async def send_task4(background_tasks: BackgroundTasks):
    background_tasks.add_task(task3.delay)
    return
