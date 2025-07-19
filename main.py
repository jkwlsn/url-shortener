import asyncio

from dotenv import dotenv_values
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

"""Get settings from .env"""
SETTINGS: dict[str, str | None] = {**dotenv_values(dotenv_path=".env")}

"""Construct database connection string"""
db: dict[str, str | None] = {
    "host": SETTINGS["POSTGRES_HOST"],
    "port": SETTINGS["POSTGRES_PORT"],
    "user": SETTINGS["POSTGRES_USER"],
    "password": SETTINGS["POSTGRES_PASSWORD"],
    "dbname": SETTINGS["POSTGRES_DB"],
}

DATABASE_URL: str = f"postgresql+psycopg_async://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['dbname']}"

""" Establish async connection to database """
asyncio_engine: AsyncEngine = create_async_engine(url=DATABASE_URL, echo=True)

async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=asyncio_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def main() -> None:
    pass


if __name__ == "__main__":
    main()
