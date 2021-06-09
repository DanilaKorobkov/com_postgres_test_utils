import asyncio
from contextlib import asynccontextmanager, contextmanager
from typing import Iterator

import asyncpg
import attr
import docker
from yarl import URL


@attr.s(auto_attribs=True, slots=True, frozen=True)
class PostgresConfig:
    host: str
    port: int
    user_name: str
    user_password: str
    database_name: str

    def get_postgres_docker_env(self) -> dict[str, str]:
        return {
            "POSTGRES_USER": self.user_name,
            "POSTGRES_PASSWORD": self.user_password,
            "POSTGRES_DB": self.database_name,
        }

    def get_url(self) -> URL:
        return URL.build(
            scheme="postgresql",
            user=self.user_name,
            password=self.user_password,
            host=self.host,
            port=self.port,
            path=f"/{self.database_name}",
        )


@contextmanager
def up_postgres_container(config: PostgresConfig) -> Iterator[None]:
    docker_client = docker.from_env()

    container = docker_client.containers.run(
        image="postgres:13-alpine",
        detach=True,
        environment=config.get_postgres_docker_env(),
        ports={
            "5432/tcp": (config.host, config.port),
        },
    )
    try:
        yield
    finally:
        container.remove(force=True)
        docker_client.close()


@asynccontextmanager
async def up_postgres_pool(url: URL) -> asyncpg.Pool:
    await _wait_postgres_setup(url)
    async with asyncpg.create_pool(str(url)) as pool:
        try:
            yield pool
        finally:
            await pool.close()


async def _wait_postgres_setup(url: URL) -> None:
    for _ in range(50):
        try:
            await asyncpg.connect(str(url))
        except ConnectionError:
            await asyncio.sleep(0.05)
        else:
            return
    raise RuntimeError("Could not connect to the Postgres")
