r"""
https://api.video/blog/tutorials/uploading-large-files-with-javascript
"""
import time
from typing import Optional

from starlette.requests import Request
from starlette.responses import StreamingResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, File, UploadFile
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

templates = Jinja2Templates(directory='./templates/')

@app.get('/')
async def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


@app.post('/files/')
async def upload_files(f: bytes = File(...)):
    return {'size': len(f)}


@app.post('/upload/')
async def upload_file(f: UploadFile = File(...)):
    st = time.time()
    fname = f.filename
    print(fname)
    print(f.content_type)
    cont = await f.read()
    print(time.time()-st)
