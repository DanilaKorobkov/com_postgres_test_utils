# pylint: disable=redefined-outer-name

import asyncio
import secrets
from typing import AsyncIterator, Final, Iterator

import asyncpg
import pytest
from aiohttp.test_utils import unused_port
from yarl import URL

from .utils import PostgresConfig, up_postgres_container, up_postgres_pool

pytest_plugins: Final = ("aiohttp.pytest_plugin",)


@pytest.fixture(scope="session")
def com_postgres_config() -> PostgresConfig:
    return PostgresConfig(
        host="127.0.0.1",
        port=unused_port(),
        user_name="user",
        user_password=secrets.token_urlsafe(nbytes=10),
        database_name="demo",
    )


@pytest.fixture(scope="session")
def com_postgres_url(com_postgres_config: PostgresConfig) -> Iterator[URL]:
    with up_postgres_container(com_postgres_config):
        yield com_postgres_config.get_url()


@pytest.fixture
async def com_postgres_pool(
    com_postgres_url: URL,
    loop: asyncio.AbstractEventLoop,
) -> AsyncIterator[asyncpg.Connection]:
    assert loop.is_running()

    async with up_postgres_pool(com_postgres_url) as pool:
        yield pool
