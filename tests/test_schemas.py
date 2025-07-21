import pytest
from pydantic import HttpUrl, ValidationError

from config.config import settings
from schemas.schemas import LongUrlAccept, ShortUrlReturn

slug = "A1b2C3d"
invalid_url = "an-invalid-url"
long_url = "https://example.com/a/deep/page/and-some-more-information-here.html"
self_reference_url = f"{settings.base_url}an-example-url"
valid_short_url = f"{settings.base_url}{slug}"


class TestPydantic:
    """Test suite for Pydantic schemas"""

    def test_accept_valid_long_urls(self) -> None:
        """Valid urls should be accepted"""
        data: dict[str, str] = {"long_url": long_url}

        schema: LongUrlAccept = LongUrlAccept(**data)

        assert isinstance(schema.long_url, HttpUrl)
        assert str(schema.long_url) == long_url

    def test_do_not_accept_invalid_long_urls(self) -> None:
        """Invalid urls should raise ValidationErrors"""
        invalid_data: dict[str, str] = {"long_url": invalid_url}

        with pytest.raises(ValidationError) as e:
            schema: LongUrlAccept = LongUrlAccept(**invalid_data)

        assert "long_url" in str(e.value)

    def test_do_not_accept_recursive_long_urls(self) -> None:
        """URLs from the same host should be rejected to prevent loops"""
        invalid_data: dict[str, str] = {"long_url": self_reference_url}

        with pytest.raises(ValidationError) as e:
            schema: LongUrlAccept = LongUrlAccept(**invalid_data)

        assert "long_url" in str(e.value)

    def test_pydantic_model_accept_valid_short_url(self) -> None:
        """The ShortUrlReturn model should accept valid short urls"""
        data: dict[str, str] = {"short_url": valid_short_url}

        schema: ShortUrlReturn = ShortUrlReturn(**data)

        assert isinstance(schema.short_url, HttpUrl)
        assert str(schema.short_url) == valid_short_url

    def test_pydantic_model_reject_invalid_short_url(self) -> None:
        """The ShortUrlReturn model should reject invalid short urls"""
        invalid_data: dict[str, str] = {"short_url": invalid_url}

        with pytest.raises(ValidationError) as e:
            ShortUrlReturn(**invalid_data)

        assert "short_url" in str(e.value)
