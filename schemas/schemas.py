"""Pydantic models"""

from pydantic import BaseModel, HttpUrl, field_validator

from config.config import settings
from exceptions.exceptions import (
    SelfReferencingURLError,
    URLTooLongError,
    URLTooShortError,
)


class LongUrlAccept(BaseModel):
    long_url: HttpUrl

    @field_validator("long_url", mode="before")
    @classmethod
    def validate_length(cls, long_url: str) -> str:
        if len(long_url) > settings.max_url_length:
            raise URLTooLongError(long_url, settings.max_url_length)
        if len(long_url) < settings.min_url_length:
            raise URLTooShortError(long_url, settings.min_url_length)
        return long_url

    @field_validator("long_url")
    @classmethod
    def validate_reject_same_domain(cls, long_url: HttpUrl) -> HttpUrl:
        if str(long_url.host) in str(settings.base_url):
            raise SelfReferencingURLError(str(long_url))
        return long_url


class ShortUrlReturn(BaseModel):
    short_url: HttpUrl
