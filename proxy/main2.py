import time
from typing import Optional

from starlette.requests import Request
from starlette.responses import StreamingResponse, Response
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


origins = [
    "http://127.0.0.1",
    "http://127.0.0.1:5004",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
async def index():
    return 'hello'
