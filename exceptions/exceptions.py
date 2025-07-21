"""Custom errors"""


class URLTooLongError(ValueError):
    def __init__(self, url: str, limit: int) -> None:
        super().__init__(f"URL exceeds max length of {limit} characters: {url}")


class URLTooShortError(ValueError):
    def __init__(self, url: str, minimum: int) -> None:
        super().__init__(f"URL shorter than minimum {minimum} characters: {url}")


class SelfReferencingURLError(ValueError):
    def __init__(self, url: str) -> None:
        super().__init__(f"Cannot shorten URLs pointing to the service itself: {url}")


class NoMatchingSlugError(Exception):
    def __init__(self, slug: str) -> None:
        super().__init__(f"{slug} does not exist")


class LinkExpiredError(Exception):
    def __init__(self, slug: str, max_url_age: int) -> None:
        super().__init__(f"{slug} has expired: older than {max_url_age} days old.")
