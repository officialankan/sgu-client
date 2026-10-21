"""Shared fixtures: a client wired to an in-memory transport."""

import pytest

from sgu_client import SGUClient
from tests.fakes import FakeTransport


@pytest.fixture
def fake() -> FakeTransport:
    return FakeTransport()


@pytest.fixture
def client(fake: FakeTransport) -> SGUClient:
    return SGUClient(transport=fake)
