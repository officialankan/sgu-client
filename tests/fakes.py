"""In-memory transport for tests: canned SGU responses, no network."""

import json
from dataclasses import dataclass
from typing import Any

from sgu_client import TransportResponse

Response = dict[str, Any] | TransportResponse | Exception
"""A dict is sent as a 200 JSON body, an exception is raised."""


@dataclass(frozen=True)
class Request:
    url: str
    params: dict[str, Any]


class FakeTransport:
    """Serves queued responses by route and records every request.

    A route is the end of a URL, e.g. ``"collections/stationer/items"``. When
    several routes match a URL, the longest wins. A request with no matching
    route, or whose route has run out of responses, fails the test.
    """

    def __init__(self, routes: dict[str, Response | list[Response]] | None = None):
        self._routes: dict[str, list[Response]] = {}
        self.requests: list[Request] = []
        self.closed = False
        for route, responses in (routes or {}).items():
            self.add(
                route, *(responses if isinstance(responses, list) else [responses])
            )

    def add(self, route: str, *responses: Response) -> None:
        """Queue responses for a route, after any already queued."""
        self._routes.setdefault(route, []).extend(responses)

    @property
    def params(self) -> dict[str, Any]:
        """Params of the last request."""
        return self.requests[-1].params

    def close(self) -> None:
        self.closed = True

    def fetch(self, url: str, params: dict[str, Any]) -> TransportResponse:
        self.requests.append(Request(url, dict(params)))
        matches = [route for route in self._routes if url.endswith(route)]
        if not matches:
            raise AssertionError(f"unexpected request: {url} {params}")
        route = max(matches, key=len)
        if not self._routes[route]:
            raise AssertionError(f"no responses left for {route}: {url} {params}")
        response = self._routes[route].pop(0)
        if isinstance(response, Exception):
            raise response
        if isinstance(response, TransportResponse):
            return response
        return TransportResponse(200, json.dumps(response))


def paged(
    features: list[dict[str, Any]],
    page_size: int,
    number_matched: int | str | None = None,
) -> list[dict[str, Any]]:
    """Split features into the pages SGU would return, page_size features each.

    ``number_matched`` defaults to the number of features; pass ``"unknown"``
    to mimic SGU when it doesn't count.
    """
    matched = len(features) if number_matched is None else number_matched
    chunks = [features[i : i + page_size] for i in range(0, len(features), page_size)]
    return [
        {
            "type": "FeatureCollection",
            "features": chunk,
            "numberReturned": len(chunk),
            "numberMatched": matched,
            "totalFeatures": matched,
            "timeStamp": "2024-01-01T12:00:00Z",
            "links": [],
        }
        for chunk in chunks or [[]]
    ]
