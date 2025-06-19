import asyncpg
from urllib.parse import urlparse
from app.config.config import settings

async def ensure_database_exists():
    db_url = settings.database_url

    parsed_url = urlparse(db_url)

    db_name = parsed_url.path[1:]
    user = parsed_url.username
    password = parsed_url.password
    host = parsed_url.hostname
    port = parsed_url.port

    conn = await asyncpg.connect(
        user=user,
        password=password,
        database="postgres",
        host=host,
        port=port
    )

    result = await conn.fetchval(
        "SELECT 1 FROM pg_database WHERE datname = $1", db_name
    )

    if not result:
        await conn.execute(f'CREATE DATABASE "{db_name}"')
        print(f"Database '{db_name}' created.")
    else:
        print(f"Database '{db_name}' already exists.")

    await conn.close()
