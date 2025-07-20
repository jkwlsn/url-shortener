from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import (
    NoMatchingSlugError,
)
from main import *
from models import Link
from services.long_url import get_long_url


class TestLongUrlService:
    @pytest.mark.asyncio
    async def test_get_long_url_by_slug_success(self) -> None:
        """If there is a slug and a matching long_url in the database, we should be able to find it"""
        slug = "A1b2C3d"
        long_url = "https://example.com/a/deep/page/and-some-more-information-here.html"
        test_link: Link = Link(link_id=1, slug=slug, long_url=long_url)
        mock_db: AsyncMock = AsyncMock(AsyncSession)
        mock_db.scalar.return_value = test_link

        result = await get_long_url(mock_db, slug)

        assert result == long_url
        assert mock_db.scalar.await_count == 1

    @pytest.mark.asyncio
    async def test_get_long_url_by_slug_failure(self) -> None:
        """If there is no matching slug in the database, we should return an error"""
        slug = "an-invalid-slug"
        mock_db = AsyncMock(AsyncSession)
        mock_db.scalar.return_value = None

        with pytest.raises(NoMatchingSlugError) as e:
            await get_long_url(mock_db, slug)

        assert "slug" in str(e.value)
