import asyncio
import asyncpg
async def main():
    conn = await asyncpg.connect('postgresql://postgres:postgres@localhost:5432/postgres')
    await conn.execute('CREATE DATABASE sladesk')
    await conn.close()
asyncio.run(main())
