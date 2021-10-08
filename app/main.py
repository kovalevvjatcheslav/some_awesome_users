from fastapi import FastAPI

from app.database import pg_session
from app.routers.users import router as users_router

app = FastAPI(
    on_startup=[pg_session.init_engine],
    on_shutdown=[pg_session.dispose_engine],
)
app.include_router(users_router)
