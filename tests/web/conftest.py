import asyncio
import pytest
import pytest_asyncio


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop for web tests."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()
