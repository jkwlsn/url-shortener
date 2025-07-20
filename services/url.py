"""Service for URL-related operations."""

import secrets
import string

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.config import settings
from exceptions.exceptions import NoMatchingSlugError
from models.models import Link


class UrlService:
    """Service class for handling URL shortening and retrieval."""

    async def get_long_url(self, db: AsyncSession, slug: str) -> str:
        """
        Retrieves the long URL associated with a given slug.

        Args:
            db: The database session.
            slug: The slug to look up.

        Returns:
            The long URL.

        Raises:
            NoMatchingSlugError: If no matching slug is found.
        """
        result: Link | None = await db.scalar(select(Link).where(Link.slug == slug))
        if not result:
            raise NoMatchingSlugError(slug)
        return str(result.long_url)

    async def create_short_url(self, db: AsyncSession, long_url: str) -> str:
        """
        Creates a short URL for a given long URL.

        Args:
            db: The database session.
            long_url: The long URL to shorten.

        Returns:
            The shortened URL.
        """
        slug: str = await self._generate_unique_slug(db)
        link = Link(slug=slug, long_url=long_url)
        db.add(link)
        await db.commit()
        await db.refresh(link)
        return f"{settings.base_url}{slug}"

    @staticmethod
    def _generate_slug(length: int) -> str:
        """
        Generates a random slug of a given length.

        Args:
            length: The desired length of the slug.

        Returns:
            A random slug.
        """
        base62: str = string.ascii_letters + string.digits
        return "".join(secrets.choice(seq=base62) for _ in range(length))

    async def _generate_unique_slug(self, db: AsyncSession) -> str:
        """
        Generates a unique slug.

        Args:
            db: The database session.

        Returns:
            A unique slug.
        """
        while True:
            slug: str = self._generate_slug(settings.slug_length)
            slug_exists: Link | None = await db.scalar(
                select(Link).where(Link.slug == slug)
            )
            if not slug_exists:
                return slug
