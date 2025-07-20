import re
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from main import *
from services.short_url import (
    create_short_url,
    generate_slug,
    generate_unique_slug,
)


class TestShortUrlService:
    def test_generate_valid_slug(self) -> None:
        """Generated slugs should be 7 upper and lower alphanumeric characters"""
        result: str = generate_slug(7)

        assert re.match(pattern="^[A-Za-z0-9]{7}$", string=result)

    @pytest.mark.asyncio
    async def test_generate_unique_slug_no_collision(self) -> None:
        """Ensure slugs are be unique

        This test will run ONCE to simulate the successful creation of a unique slug."""
        mock_db: AsyncMock = AsyncMock(AsyncSession)
        mock_db.scalar.return_value = None

        slug: str = await generate_unique_slug(mock_db)

        assert isinstance(slug, str)
        assert len(slug) == 7
        assert mock_db.scalar.await_count == 1

    @pytest.mark.asyncio
    async def test_generate_unique_slug_one_collision(self) -> None:
        """Ensure slugs are be unique

        This test will run TWICE to simulate the successful creation of a non-unique and then unique slug."""
        mock_db: AsyncMock = AsyncMock(AsyncSession)

        mock_db.scalar.side_effect = ["ABCDEFG", None]

        slug: str = await generate_unique_slug(mock_db)

        assert isinstance(slug, str)
        assert len(slug) == 7
        assert mock_db.scalar.await_count == 2

    @pytest.mark.asyncio
    @patch("services.short_url.generate_unique_slug", new_callable=AsyncMock)
    async def test_short_url(self, mock_generate_unique_slug: MagicMock) -> None:
        """Ensure valid short URLs are created

        The random slug should be appended to the base_url defined in .env"""
        mock_db: AsyncMock = AsyncMock(AsyncSession)
        mock_generate_unique_slug.return_value = "A1b2C3d"
        long_url = "https://example.com/a/deep/page/and-some-more-information-here.html"

        short_url: str = await create_short_url(mock_db, long_url)

        assert isinstance(short_url, str)
        assert short_url == "https://jkwlsn.dev/A1b2C3d"
