from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from config.config import settings
from database.database import create_tables
from routes.routes import router as shorten_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator:
    await create_tables()
    yield


app: FastAPI = FastAPI(title=settings.app_name)

app.include_router(shorten_router)
