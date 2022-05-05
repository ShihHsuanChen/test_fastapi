import asyncio
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.background import BackgroundTasks

from app import task2


origins = [
    "http://localhost",
    "http://localhost:8080",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def task1():
    print('async task')
    await asyncio.sleep(2)
    now = datetime.now()
    print(now)
    return now


@app.get('/task1')
async def send_task1(background_tasks: BackgroundTasks):
    background_tasks.add_task(task1)
    return


@app.get('/task2')
async def send_task2(background_tasks: BackgroundTasks):
    background_tasks.add_task(task2.delay)
    return


@app.get('/task3')
async def send_task3(background_tasks: BackgroundTasks):
    from tasks import task3
    background_tasks.add_task(task3.delay)
    return


import router

app.include_router(router.router, prefix='/r')
