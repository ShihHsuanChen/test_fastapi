from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from configs import cfg
import routers


app = FastAPI(title='FastAPI with VueJS', root_path=cfg.root_path)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost',
        'http://localhost:8080',
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.mount('/asset', routers.staticfiles)
app.include_router(routers.get_router(cfg), tags=['ui'])
