import os
import json
from fastapi import APIRouter, Request
from fastapi.responses import Response, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


MEDIA_TYPE_MAP = {
    'js': 'application/javascript',
    'html': None,
    'svg': None,
    'png': None,
    'jpg': None,
    'ico': None,
    'css': None,
}


staticfiles = StaticFiles(directory='./frontend/asset/')


def get_router(cfg):
    router = APIRouter()

    templates = Jinja2Templates(directory='./frontend/')

    @router.get('/favicon.ico')
    def render_favicon(request: Request):
        return FileResponse('./frontend/favicon.ico')

    @router.get('/', response_class=HTMLResponse, name='root')
    def render_root(request: Request):
        path = 'index.html'
        params = {'request': request}
        params.update({k.upper(): json.dumps(v) for k, v in cfg.dict().items()})
        resp = templates.TemplateResponse(path, params)
        return resp

    @router.get('/{full_path:path}', response_class=Response)
    def render_scripts(request: Request, full_path: str):
        params = {'request': request}
        params.update({k.upper(): v for k, v in cfg.dict().items()})
        media_type = MEDIA_TYPE_MAP.get(full_path.split('.')[-1])
        resp = templates.TemplateResponse(full_path, params, media_type=media_type)
        return resp

    return router
