import pytest
from sqlalchemy import text

from main import async_session, main


class TestMain:
    def test_main_returns_none(self) -> None:
        assert main() is None

    @pytest.mark.asyncio
    async def test_database_async_connection(self) -> None:
        async with async_session() as session:
            result = await session.execute(text("SELECT 1"))
            value = result.scalar()

            assert value == 1, (
                "Database connection failed or returned unexpected result"
            )
