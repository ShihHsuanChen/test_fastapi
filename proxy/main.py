r"""
https://github.com/tiangolo/fastapi/issues/1788
"""
import time
from typing import Optional

from starlette.requests import Request
from starlette.responses import StreamingResponse, Response
from starlette.background import BackgroundTask

from fastapi import FastAPI, HTTPException
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

import re
import httpx

rules = [
    {
        'regex': r'^/api/',
        'base_url': 'http://127.0.0.1:5005/',
        'replace': '/',
    },
    {
        'regex': r'^/',
        'base_url': 'http://127.0.0.1:5006/',
        'replace': '/',
    },
]

async def _reverse_proxy(request: Request):
    url = request.url.path
    for rule in rules:
        if re.match(rule['regex'], url):
            new_url = re.sub(rule['regex'], rule['replace'], url, count=1)
            base_url = rule['base_url']
            break
    else:
        return HTTPException(status_code=502)
        
    new_url = httpx.URL(
        path=new_url,
        query=request.url.query.encode("utf-8")
    )
    client = httpx.AsyncClient(base_url=base_url)
    rp_req = client.build_request(
        request.method, new_url,
        headers=request.headers.raw,
        content=await request.body(),
    )
    rp_resp = await client.send(rp_req, stream=True)

    return StreamingResponse(
        rp_resp.aiter_raw(),
        status_code=rp_resp.status_code,
        headers=rp_resp.headers,
        background=BackgroundTask(rp_resp.aclose),
    )

app.add_route("/{path:path}", _reverse_proxy, ["GET", "POST"])
