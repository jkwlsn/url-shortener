import os

from dotenv import dotenv_values

SETTINGS: dict[str, str | None] = {**dotenv_values(".env")}


def main() -> None:
    pass


if __name__ == "__main__":
    main()
