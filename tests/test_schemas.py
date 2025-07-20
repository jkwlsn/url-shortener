import pytest
from pydantic import HttpUrl, ValidationError

from main import *
from schemas import LongUrlAccept, LongUrlReturn, ShortUrlReturn


class TestPydantic:
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

    def test_pydantic_model_accept_valid_short_url(self) -> None:
        """The ShortUrlReturn model should accept valid short urls"""
        data: dict[str, str] = {"short_url": "https://jkwlsn.dev/A1b2C3d"}

        schema: ShortUrlReturn = ShortUrlReturn(**data)

        assert isinstance(schema.short_url, HttpUrl)
        assert str(schema.short_url) == "https://jkwlsn.dev/A1b2C3d"

    def test_pydantic_model_reject_invalid_short_url(self) -> None:
        """The ShortUrlReturn model should reject invalid short urls"""
        invalid_data: dict[str, str] = {"short_url": "an-invalid-url"}

        with pytest.raises(ValidationError) as e:
            ShortUrlReturn(**invalid_data)

        assert "validation error" in str(e.value)
