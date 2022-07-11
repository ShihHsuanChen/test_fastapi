import os
from fastapi import FastAPI, APIRouter, Query, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

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

router = APIRouter()


import time

def sleeptask(uid):
    print('do task:', uid)
    time.sleep(1)
    print('task finished:', uid)


@router.get("/something")
async def get_something(
        background_tasks: BackgroundTasks,
        something_id: int = Query(1, description="Some description"),
        full: bool = Query(False, description="Some description"),
    ):
    # ... do some database queries or whatever
    background_tasks.add_task(sleeptask, something_id)
    return {"something_id": something_id, "full": full}


@router.get("/two_somethings")
async def get_two_somethings(
        background_tasks: BackgroundTasks,
        something_id_1: int = Query(1, description="Some description"),
        something_id_2: int = Query(2, description="Some description"),
    ):
    one = await get_something(background_tasks, something_id_1)
    two = await get_something(background_tasks, something_id_2)
    return {"one": one, "two": two}


sub_router = APIRouter()

@sub_router.get("/foo")
async def get_foo():
    return 'foo'


@sub_router.get("/goo")
async def get_goo():
    return 'goo'

router.include_router(sub_router, prefix='/sub')

app.include_router(router)
