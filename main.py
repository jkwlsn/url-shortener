
from dotenv import dotenv_values

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


def main() -> None:
    pass


if __name__ == "__main__":
    main()
