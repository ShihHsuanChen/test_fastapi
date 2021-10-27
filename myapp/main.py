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


def main():
    import uvicorn
    uvicorn.run(app, host=os.getenv('WS_HOST', '127.0.0.1'), port=int(os.getenv('WS_PORT', '8000')))
