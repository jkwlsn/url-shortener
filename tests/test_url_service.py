import re
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import NoMatchingSlugError
from models import Link
from services.url import UrlService


class TestUrlService:
    """Test suite for the UrlService class."""

    def test_generate_valid_slug(self) -> None:
        """Ensure that generated slugs are valid."""
        slug = UrlService._generate_slug(7)
        assert re.match(r"^[A-Za-z0-9]{7}$", slug)

    @pytest.mark.asyncio
    async def test_generate_unique_slug_no_collision(self) -> None:
        """Test that a unique slug is generated without collisions."""
        mock_db = AsyncMock(AsyncSession)
        mock_db.scalar.return_value = None
        slug = await UrlService()._generate_unique_slug(mock_db)
        assert isinstance(slug, str)
        assert len(slug) == 7
        assert mock_db.scalar.await_count == 1

    @pytest.mark.asyncio
    async def test_generate_unique_slug_one_collision(self) -> None:
        """Test that a unique slug is generated after one collision."""
        mock_db = AsyncMock(AsyncSession)
        mock_db.scalar.side_effect = ["ABCDEFG", None]
        slug = await UrlService()._generate_unique_slug(mock_db)
        assert isinstance(slug, str)
        assert len(slug) == 7
        assert mock_db.scalar.await_count == 2

    @pytest.mark.asyncio
    @patch("services.url.UrlService._generate_unique_slug", new_callable=AsyncMock)
    async def test_create_short_url(self, mock_generate_unique_slug: MagicMock) -> None:
        """Test that a short URL is created successfully."""
        mock_db = AsyncMock(AsyncSession)
        mock_generate_unique_slug.return_value = "A1b2C3d"
        long_url = "https://example.com/a/deep/page/and-some-more-information-here.html"
        short_url = await UrlService().create_short_url(mock_db, long_url)
        assert isinstance(short_url, str)
        assert short_url == "https://jkwlsn.dev/A1b2C3d"

    @pytest.mark.asyncio
    async def test_get_long_url_by_slug_success(self) -> None:
        """Test that a long URL can be retrieved by its slug."""
        slug = "A1b2C3d"
        long_url = "https://example.com/a/deep/page/and-some-more-information-here.html"
        test_link = Link(link_id=1, slug=slug, long_url=long_url)
        mock_db = AsyncMock(AsyncSession)
        mock_db.scalar.return_value = test_link
        result = await UrlService().get_long_url(mock_db, slug)
        assert result == long_url
        assert mock_db.scalar.await_count == 1

    @pytest.mark.asyncio
    async def test_get_long_url_by_slug_failure(self) -> None:
        """Test that an error is raised when a slug is not found."""
        slug = "an-invalid-slug"
        mock_db = AsyncMock(AsyncSession)
        mock_db.scalar.return_value = None
        with pytest.raises(NoMatchingSlugError) as e:
            await UrlService().get_long_url(mock_db, slug)
        assert "slug" in str(e.value)
