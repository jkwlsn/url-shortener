import re
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
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

    def test_do_not_accept_recursive_long_urls(self) -> None:
        """URLs from the same host should be rejected to prevent loops"""
        invalid_data: dict[str, str] = {"long_url": "https://jkwlsn.dev/an-example-url"}

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

    @pytest.mark.asyncio
    async def test_long_url_with_matching_slug(self) -> None:
        slug = "A1b2C3d"
        long_url = "https://example.com/a/deep/page/and-some-more-information-here.html"
        test_link = Link(link_id=1, slug=slug, long_url=long_url)
        mock_db = AsyncMock(AsyncSession)
        mock_db.scalar.return_value = test_link

        result = await get_long_url(mock_db, slug)

        assert result == long_url
        assert mock_db.scalar.await_count == 1

    @pytest.mark.asyncio
    async def test_long_url_no_matching_slug(self) -> None:
        slug = "an-invalid-slug"
        mock_db = AsyncMock(AsyncSession)
        mock_db.scalar.return_value = None

        with pytest.raises(NoMatchingSlugError) as e:
            await get_long_url(mock_db, slug)

        assert "slug" in str(e.value)

    """ FastAPI Routes """

    @pytest.mark.asyncio
    async def test_root(self) -> None:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            response = await ac.get("/")

        assert response.status_code == 200

    @pytest.mark.asyncio
    @patch("main.generate_short_url", new_callable=AsyncMock)
    async def test_create_short_url_valid_long_url(
        self, mock_generate_short_url: MagicMock
    ) -> None:
        mock_generate_short_url.return_value = "https://jkwlsn.dev/A1b2C3d"
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            payload = {"long_url": "https://www.example.com/page"}
            response = await ac.post(url="/shorten", json=payload)

        assert response.status_code == 200
        assert response.json() == {"short_url": "https://jkwlsn.dev/A1b2C3d"}

    @pytest.mark.asyncio
    async def test_can_not_create_short_url_invalid_long_url(self) -> None:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            payload = {"long_url": "an-invalid-url"}
            response = await ac.post(url="/shorten", json=payload)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_can_not_create_short_url_long_url_too_long(self) -> None:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            payload = {"long_url": f"https://www.example.com/{'a' * 2500}"}
            response = await ac.post(url="/shorten", json=payload)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_can_not_create_short_url_long_url_too_short(self) -> None:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            payload = {"long_url": "http://bit.ly/"}
            response = await ac.post(url="/shorten", json=payload)

        assert response.status_code == 422
        assert "long_url" in response.text

    @pytest.mark.asyncio
    @patch("main.get_long_url", new_callable=AsyncMock)
    async def test_return_long_url_for_valid_slug(
        self, mock_get_long_url: MagicMock
    ) -> None:
        mock_get_long_url.return_value = "https://www.example.com/page"
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            response = await ac.get(url="/ABCD123")

        assert response.status_code == 307
        assert response.is_redirect

    @pytest.mark.asyncio
    @patch("main.get_long_url", new_callable=AsyncMock)
    async def test_return_error_for_invalid_slug(
        self, mock_get_long_url: MagicMock
    ) -> None:
        mock_get_long_url.side_effect = NoMatchingSlugError("No matching slug found")
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            response = await ac.get(url="/ABCD123")

        assert response.status_code == 404
