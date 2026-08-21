from urllib.parse import urljoin, urlsplit, urlunsplit

_LOCAL_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})


def absolute_image_url(path: str, *, public_base_url: str) -> str:
    """Return an absolute image URL and require HTTPS for public hosts."""
    url = (
        path
        if path.startswith(("http://", "https://"))
        else urljoin(f"{public_base_url.rstrip('/')}/", path.lstrip("/"))
    )
    parsed = urlsplit(url)
    if parsed.scheme == "http" and parsed.hostname not in _LOCAL_HOSTS:
        return urlunsplit(parsed._replace(scheme="https"))
    return url
