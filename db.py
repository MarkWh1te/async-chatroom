import asyncio
from random import randint
from aiomysql.sa import create_engine
import sqlalchemy as sa
from sqlalchemy.sql import select
from aiohttp_session import SimpleCookieStorage, session_middleware
from aiohttp_security import has_permission, \
    is_anonymous, remember, forget, \
    setup as setup_security, SessionIdentityPolicy
from aiohttp_security.abc import AbstractAuthorizationPolicy

metadata = sa.MetaData()

User = sa.Table('users',
                metadata,
                sa.Column('id', sa.Integer, primary_key=True),
                sa.Column('name', sa.String(255), nullable=False),
                sa.Column('password', sa.String(255), nullable=False),
                )


async def create_table(engine):
    async with engine.acquire() as conn:
        await conn.execute('DROP TABLE IF EXISTS users')
        create_user_sql = """
        CREATE TABLE users (
        id INTEGER NOT NULL,
        name VARCHAR(255),
        password VARCHAR(255),
        PRIMARY KEY (id)
        )
        """
        await conn.execute(create_user_sql)


async def init_admin_user(loop):
    engine = await create_engine(host='markwh1te.club', password='ApgrmWrmzcf8ZV8Dxh', port=8868, user='46ujzA1rRkeWEdviMzxfX', db='blog', loop=loop)
    # await create_table(engine)
    async with engine.acquire() as conn:
        await conn.execute(User.insert().values(
            id=randint(1, 1000000),
            name="admin",
            password=f"wangdagua{randint(1,1000)}"
        )
        )
        res = await conn.execute(select([User]))
        # res = await conn.execute(User.select())
        res = await res.fetchall()
        for row in res:
            print(f"admin name:{row.name}\nadmin password:{row.password}")

    engine.close()
    await engine.wait_closed()


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_admin_user(loop))


if __name__ == '__main__':
    main()
