from fastapi import FastAPI, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import pg_session
from app.routers.users import router as users_router
from app.utils import InvalidTokenException, TokenExpiredException

app = FastAPI(
    on_startup=[pg_session.init_engine],
    on_shutdown=[pg_session.dispose_engine],
)
app.include_router(users_router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


@app.exception_handler(InvalidTokenException)
@app.exception_handler(TokenExpiredException)
async def token_exception_handler(request, exc):
    resp = await http_exception_handler(request, exc)
    resp.delete_cookie("token")
    return resp


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
