"""FastAPI Routes"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from exceptions.exceptions import LinkExpiredError, NoMatchingSlugError
from main import app


class TestRoutes:
    @pytest.mark.asyncio
    async def test_root(self) -> None:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            response = await ac.get("/")

        assert response.status_code == 200

    @pytest.mark.asyncio
    @patch("services.url.UrlService.create_short_url", new_callable=AsyncMock)
    async def test_return_short_url_valid_long_url(
        self, mock_create_short_url: MagicMock
    ) -> None:
        mock_create_short_url.return_value = "https://jkwlsn.dev/A1b2C3d"
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            payload = {"long_url": "https://www.example.com/page"}
            response = await ac.post(url="/shorten", json=payload)

        assert response.status_code == 200
        assert response.json() == {"short_url": "https://jkwlsn.dev/A1b2C3d"}

    @pytest.mark.asyncio
    async def test_can_not_return_short_url_invalid_long_url(self) -> None:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            payload = {"long_url": "an-invalid-url"}
            response = await ac.post(url="/shorten", json=payload)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_can_not_return_short_url_long_url_too_long(self) -> None:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            payload = {"long_url": f"https://www.example.com/{'a' * 2500}"}
            response = await ac.post(url="/shorten", json=payload)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_can_not_return_short_url_long_url_too_short(self) -> None:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            payload = {"long_url": "http://bit.ly/"}
            response = await ac.post(url="/shorten", json=payload)

        assert response.status_code == 422
        assert "long_url" in response.text

    @pytest.mark.asyncio
    @patch("services.url.UrlService.create_short_url", new_callable=AsyncMock)
    async def test_can_not_return_short_url_internal_error(
        self, mock_create_short_url: MagicMock
    ) -> None:
        mock_create_short_url.side_effect = Exception("Internal error")
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            payload = {"long_url": "https://www.example.com/page"}
            response = await ac.post(url="/shorten", json=payload)

        assert response.status_code == 500
        assert "Internal error" in response.text

    @pytest.mark.asyncio
    @patch("services.url.UrlService.get_long_url", new_callable=AsyncMock)
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
    @patch("services.url.UrlService.get_long_url", new_callable=AsyncMock)
    async def test_return_error_for_invalid_slug(
        self, mock_get_long_url: MagicMock
    ) -> None:
        mock_get_long_url.side_effect = NoMatchingSlugError("No matching slug found")
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            response = await ac.get(url="/ABCD123")

        assert response.status_code == 404

    @pytest.mark.asyncio
    @patch("services.url.UrlService.get_long_url", new_callable=AsyncMock)
    async def test_return_error_for_expired_link(
        self, mock_get_long_url: MagicMock
    ) -> None:
        mock_get_long_url.side_effect = LinkExpiredError("ABCD123")
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            response = await ac.get(url="/ABCD123")
        assert response.status_code == 410
        assert response.json() == {
            "detail": "ABCD123 has expired: older than 30 days old."
        }
