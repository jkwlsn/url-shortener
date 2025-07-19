import re
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import HttpUrl, ValidationError
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from main import *


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

    """Test suite for Pydantic schemas"""

    def test_accept_valid_long_urls(self) -> None:
        """Valid urls should be accepted"""
        data: dict[str, str] = {
            "long_url": "https://example.com/a/deep/page/and-some-more-information-here.html"
        }

        schema: LongUrlAccept = LongUrlAccept(**data)

        assert isinstance(schema.long_url, HttpUrl)
        assert (
            str(schema.long_url)
            == "https://example.com/a/deep/page/and-some-more-information-here.html"
        )

    def test_do_not_accept_invalid_long_urls(self) -> None:
        """Invalid urls should raise ValidationErrors"""
        invalid_data: dict[str, str] = {"long_url": "an-invalid-url"}

        with pytest.raises(ValidationError) as e:
            schema: LongUrlAccept = LongUrlAccept(**invalid_data)

        assert "validation error" in str(e.value)

    def test_return_valid_long_urls(self) -> None:
        """Application should return valid URLs"""
        data: dict[str, str] = {
            "long_url": "https://example.com/a/deep/page/and-some-more-information-here.html"
        }

        schema: LongUrlReturn = LongUrlReturn(**data)

        assert isinstance(schema.long_url, HttpUrl)
        assert (
            str(schema.long_url)
            == "https://example.com/a/deep/page/and-some-more-information-here.html"
        )

    def test_do_not_return_invalid_long_urls(self) -> None:
        """Invalid short urls should not be returned"""
        invalid_data: dict = {"long_url": "an-invalid-url"}

        with pytest.raises(ValidationError) as e:
            LongUrlReturn(**invalid_data)

        assert "validation error" in str(e.value)

    def test_accept_valid_slugs(self) -> None:
        """Valid slugs should be valid"""
        data: dict[str, str] = {"slug": "A1b2C3d"}

        schema: SlugAccept = SlugAccept(**data)

        assert isinstance(schema.slug, str)
        assert str(schema.slug) == "A1b2C3d"

    def test_do_not_accept_invalid_slugs(self) -> None:
        """Invalid slugs should raise ValidationErrors"""
        invalid_data: dict[str, str] = {"slug": "an-invalid-slug"}

        with pytest.raises(ValidationError) as e:
            schema: SlugAccept = SlugAccept(**invalid_data)

        assert "validation error" in str(e.value)

    def test_return_valid_short_urls(self) -> None:
        """Application should return valid slugs"""
        data: dict[str, str] = {"short_url": "https://jkwlsn.dev/A1b2C3d"}

        schema: ShortUrlReturn = ShortUrlReturn(**data)

        assert isinstance(schema.short_url, HttpUrl)
        assert str(schema.short_url) == "https://jkwlsn.dev/A1b2C3d"

    def test_do_not_return_invalid_short_urls(self) -> None:
        """Invalid short urls should not be returned"""
        invalid_data: dict[str, str] = {"short_url": "an-invalid-url"}

        with pytest.raises(ValidationError) as e:
            ShortUrlReturn(**invalid_data)

        assert "validation error" in str(e.value)

    """ Test Slug and Short Link Service """

    def test_generate_valid_slug(self) -> None:
        result = generate_slug(7)

        assert re.match("^[A-Za-z0-9]{7}$", result)

    @pytest.mark.asyncio
    async def test_generate_unique_slug_no_clash(self) -> None:
        mock_db = AsyncMock(AsyncSession)
        mock_db.scalar.return_value = None

        slug = await generate_unique_slug(mock_db)

        assert isinstance(slug, str)
        assert len(slug) == 7
        assert mock_db.scalar.await_count == 1

    @pytest.mark.asyncio
    async def test_generate_unique_slug_does_clash(self) -> None:
        mock_db = AsyncMock(AsyncSession)

        mock_db.scalar.side_effect = ["ABCDEFG", None]

        slug = await generate_unique_slug(mock_db)

        assert isinstance(slug, str)
        assert len(slug) == 7
        assert mock_db.scalar.await_count == 2

    @pytest.mark.asyncio
    @patch("main.generate_unique_slug", new_callable=AsyncMock)
    async def test_generate_short_url(
        self, mock_generate_unique_slug: MagicMock
    ) -> None:
        mock_db = AsyncMock(AsyncSession)
        mock_generate_unique_slug.return_value = "A1b2C3d"
        long_url = "https://example.com/a/deep/page/and-some-more-information-here.html"

        short_url: str = await generate_short_url(mock_db, long_url)

        assert isinstance(short_url, str)
        assert short_url == "https://jkwlsn.dev/A1b2C3d"
