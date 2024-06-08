import asyncio
import os


from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

load_dotenv()

url = f"postgresql+asyncpg://{os.environ.get('POSTGRES_USER')}:" \
      f"{os.environ.get('POSTGRES_PASSWORD')}" \
      f"@{os.environ.get('POSTGRES_HOST')}:" \
      f"{os.environ.get('POSTGRES_PORT')}" \
      f"/{os.environ.get('POSTGRES_DB')}"

engine = create_async_engine(url, echo=True)

sessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    while True:
        try:
            async with engine.begin() as conn:
                await conn.execute(text('SELECT 1'))
            print("Database is ready!")
            break
        except Exception as e:
            print(f"Waiting for the database... ({e})")
            await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(init_db())

async def get_session():
    async with sessionLocal() as session:
        yield session
