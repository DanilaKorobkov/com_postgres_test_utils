import asyncpg


async def test__com_postgres_pool__ok(com_postgres_pool: asyncpg.Pool) -> None:
    assert await com_postgres_pool.fetchval("SELECT 2 * 2") == 4
