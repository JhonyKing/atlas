"""Allowlisted, bounded HTTP fetching with DNS-level SSRF checks."""

from __future__ import annotations

import ipaddress
import socket
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from urllib.parse import urljoin, urlparse

import httpx

from atlas.providers.ports import FetchedSource

Resolver = Callable[[str], Sequence[str]]
Clock = Callable[[], datetime]


class FetcherError(RuntimeError):
    """Safe fetch failure without response bodies or credentials."""


@dataclass(frozen=True, slots=True)
class FetchPolicy:
    allowed_hosts: frozenset[str]
    max_bytes: int = 2_000_000
    max_redirects: int = 3
    timeout_seconds: float = 20.0
    allowed_content_types: frozenset[str] = field(
        default_factory=lambda: frozenset(
            {"text/markdown", "text/plain", "text/html", "application/xhtml+xml"}
        )
    )
    user_agent: str = "ATLAS-ingestion/0.1 (+https://github.com/JhonyKing/atlas)"

    def __post_init__(self) -> None:
        if not self.allowed_hosts:
            raise ValueError("at least one allowed host is required")
        if self.max_bytes <= 0:
            raise ValueError("max_bytes must be positive")
        if self.max_redirects < 0:
            raise ValueError("max_redirects must not be negative")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")


class SafeFetcher:
    def __init__(
        self,
        *,
        client: httpx.AsyncClient,
        policy: FetchPolicy,
        resolver: Resolver | None = None,
        clock: Clock | None = None,
    ) -> None:
        self._client = client
        self._policy = policy
        self._resolver = resolver or self._resolve_host
        self._clock = clock or (lambda: datetime.now(UTC))

    async def fetch(self, url: str) -> FetchedSource:
        current_url = url
        for redirect_count in range(self._policy.max_redirects + 1):
            self._validate_destination(current_url)
            try:
                response = await self._client.get(
                    current_url,
                    follow_redirects=False,
                    headers={"user-agent": self._policy.user_agent},
                    timeout=self._policy.timeout_seconds,
                )
            except httpx.HTTPError as exc:
                raise FetcherError("source request failed") from exc

            if response.status_code in {301, 302, 303, 307, 308}:
                location = response.headers.get("location")
                if not location:
                    raise FetcherError("redirect response has no location")
                if redirect_count >= self._policy.max_redirects:
                    raise FetcherError("redirect limit exceeded")
                current_url = urljoin(current_url, location)
                self._validate_destination(current_url, is_redirect=True)
                continue

            if response.status_code >= 400:
                raise FetcherError(f"source returned HTTP {response.status_code}")

            content_type = (
                response.headers.get("content-type", "").split(";", 1)[0].strip().casefold()
            )
            if content_type not in self._policy.allowed_content_types:
                raise FetcherError("source content type is not allowed")

            declared_size = response.headers.get("content-length")
            if declared_size is not None:
                try:
                    if int(declared_size) > self._policy.max_bytes:
                        raise FetcherError("source size exceeds the connector limit")
                except ValueError as exc:
                    raise FetcherError("source content length is invalid") from exc

            content = response.content
            if len(content) > self._policy.max_bytes:
                raise FetcherError("source size exceeds the connector limit")
            return FetchedSource(
                requested_url=url,
                final_url=current_url,
                content=content,
                content_type=content_type,
                fetched_at=self._clock(),
                etag=response.headers.get("etag"),
                last_modified=response.headers.get("last-modified"),
            )

        raise FetcherError("redirect limit exceeded")

    async def aclose(self) -> None:
        await self._client.aclose()

    def _validate_destination(self, url: str, *, is_redirect: bool = False) -> None:
        parsed = urlparse(url)
        prefix = "redirect target" if is_redirect else "source URL"
        if parsed.scheme != "https":
            raise FetcherError(f"{prefix} must use HTTPS")
        if parsed.username or parsed.password or not parsed.hostname:
            raise FetcherError(f"{prefix} has invalid authority")
        host = parsed.hostname.casefold().rstrip(".")
        allowed_hosts = {item.casefold().rstrip(".") for item in self._policy.allowed_hosts}
        if host not in allowed_hosts:
            raise FetcherError(f"{prefix} host is outside the allowlist")
        try:
            addresses = self._resolver(host)
        except OSError as exc:
            raise FetcherError("source host could not be resolved") from exc
        if not addresses:
            raise FetcherError("source host has no resolved addresses")
        for address in addresses:
            try:
                ip = ipaddress.ip_address(address)
            except ValueError as exc:
                raise FetcherError("source host resolved to an invalid address") from exc
            if (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_multicast
                or ip.is_reserved
                or ip.is_unspecified
            ):
                raise FetcherError("source host resolves to a private or reserved address")

    @staticmethod
    def _resolve_host(host: str) -> tuple[str, ...]:
        return tuple(
            sorted(
                {
                    str(result[4][0])
                    for result in socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
                }
            )
        )
