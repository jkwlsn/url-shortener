from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from config import settings
from database import create_tables
from routes import router as shorten_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    await create_tables()
    yield


app: FastAPI = FastAPI(title=settings.app_name)

app.include_router(shorten_router)
