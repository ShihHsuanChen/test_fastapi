import os
from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .dependencies import get_query_token, get_token_header
from .internal import admin
from .routers import items, users

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app = FastAPI(dependencies=[Depends(get_query_token)])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/ui", StaticFiles(directory="./myapp/static", html=True), name="static")

app.include_router(users.router)
app.include_router(items.router)
app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_token_header)],
    responses={418: {"description": "I'm a teapot"}},
)


@app.get("/")
async def root():
    msg = os.environ.get('ROOT_MSG', "Hello Bigger Applications!")
    return {"message": msg}


from fastapi import BackgroundTasks
from datetime import datetime, timedelta
from functools import partial
import time

container = dict()

def update_timeout(key):
    container[key] = datetime.now()
    dt = 10
    time.sleep(dt)
    now = datetime.now()
    record = container.get(key)
    print(record)
    if isinstance(record, datetime) and (now - container[key] >= timedelta(seconds=dt)):
        container[key] = 'expired'
        print(key, 'expired')


@app.post('/timer')
def create_timer(key: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(partial(update_timeout, key))
    return datetime.now().strftime('%H:%m:%S.%f')[:-2]


@app.get('/timer')
def get_timer(key: str):
    res = container.get(key)
    if isinstance(res, datetime):
        return (res - datetime.now()).total_seconds()
    else:
        return res


def main():
    import uvicorn
    uvicorn.run(app, host=os.getenv('WS_HOST', '127.0.0.1'), port=int(os.getenv('WS_PORT', '8000')))
